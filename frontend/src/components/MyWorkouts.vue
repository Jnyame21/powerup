<script setup lang="ts">
import { computed, ref} from 'vue';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import { formatDate, formatTimeInHHMMSS, countriesData } from '@/utils/util';
import type { WorkoutType, Workout } from '@/utils/types_utils';
import TheLoader from '@/components/TheLoader.vue';
import NoData from '@/components/NoData.vue';
import pusher from '@/utils/pusher';
import axiosInstance from '@/utils/axiosInstance';
import { AxiosError } from 'axios';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()
const workoutCounter = ref(15)
const workoutTime = ref(0);
const workoutTypeItem = ref<WorkoutType | null>(null)
const workoutTypeItemVidoes = ref<HTMLVideoElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null);
const previewUrl = ref<string | null>(null);
const capturedFile = ref<File | null>(null);
const passwordVisibility = ref(false)
const userImage = ref<File | null>(null)
const form = ref({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  gender: '',
  age: null,
  height: null,
  weight: null,
  country: '',
  city: '',
  bio: '',
  password: '',
  password_confirmation: ''
})

const resetForm = () => { 
  form.value = { first_name: '', last_name: '', email: '', gender: '', age: null, height: null, weight: null, country: '', city: '', bio: '', password: '', password_confirmation: '', username: '' }
} 

const workoutTypes = computed(()=>{
  return userAuthStore.workoutTypes
})

const workoutPointsEarned = computed(()=>{
  return workoutTypeItem.value ? Number((workoutTime.value / 60) * Number(workoutTypeItem.value?.points_per_minute)).toFixed(2) : 0
})
const workoutCaloriesBurned = computed(()=>{
  return workoutTypeItem.value ? Number((workoutTime.value / 60) * Number(workoutTypeItem.value?.calories_burned_per_minute)).toFixed(2) : 0
})

const workoutTimer = ref<number | undefined>(undefined)
const startWorkoutTimer =()=> {
  if (workoutTimer.value) return;
  workoutTimer.value = setInterval(() => {
    workoutTime.value++;
  }, 1000);
  workoutTypeItemVidoes.value?.play()
}

const pauseWorkout = ()=> {
  clearInterval(workoutTimer.value);
  workoutTimer.value = undefined
  workoutTypeItemVidoes.value?.pause()
}

const cancelWorkout = ()=> {
  clearInterval(workoutTimer.value);
  workoutTimer.value = undefined
  workoutTime.value = 0;
  workoutTypeItem.value = null;
  capturedFile.value = null;
  previewUrl.value = null;
  closeOverlay('WorkingOutOverlay')
  closeOverlay('StartWorkoutOverlay')
  closeOverlay('UserSelfieOverlay')
}

const timer = ref<number | undefined>(undefined);
const startWorkout = (workout_type_item: WorkoutType)=> {
  if (!userAuthStore.isAuthenticated){
    showOverlay('UserLoginOverlay')
    return;
  }
  showOverlay('StartWorkoutOverlay', workout_type_item)
  workoutCounter.value = 15
  timer && clearInterval(timer.value);
  timer.value = setInterval(() => {
    if (workoutCounter.value > 0) {
      workoutCounter.value--;
    } 
    else {
      clearInterval(timer.value);
      timer.value = undefined;
      closeOverlay('StartWorkoutOverlay')
      showOverlay('WorkingOutOverlay', workout_type_item)
      workoutTime.value = 0;
      startWorkoutTimer()
    }
  }, 1000);
}

const skipWorkoutCounter = ()=>{
  if (!workoutTypeItem.value) return;
  clearInterval(timer.value);
  timer.value = undefined;
  closeOverlay('StartWorkoutOverlay')
  showOverlay('WorkingOutOverlay', workoutTypeItem.value)
  workoutTime.value = 0;
  startWorkoutTimer()
} 

const stopWorkout = ()=> {
  clearInterval(timer.value);
  timer.value = undefined;
  workoutTypeItem.value = null;
  closeOverlay('StartWorkoutOverlay')
}

const openCamera = () => {
  pauseWorkout()
  fileInput.value?.click();
  closeOverlay('WorkingOutOverlay')
  showOverlay('UserSelfieOverlay', workoutTypeItem.value)
};

const handleSelfie = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    capturedFile.value = file;
    previewUrl.value = URL.createObjectURL(file);
  }
};

const retakeSelfie = () => {
  capturedFile.value = null;
  previewUrl.value = null;
  fileInput.value?.click();
};

const submitWorkout = async () => {
  elementsStore.ShowLoadingOverlay()
  const formData = new FormData()
  formData.append('type', 'createWorkout')
  formData.append('workoutType', workoutTypeItem.value?.id.toString() || '')
  formData.append('duration', workoutTime.value.toString())
  formData.append('pointsEarned', workoutPointsEarned.value.toString())
  formData.append('caloriesBurned', workoutCaloriesBurned.value.toString())
  formData.append('selfie', capturedFile.value || '')
  
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const data: Workout = response.data
    userAuthStore.workoutData.unshift(data)
    capturedFile.value = null
    previewUrl.value = null
    closeOverlay('UserSelfieOverlay')    
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay(`Workout complete! You earned ${workoutPointsEarned.value} points, burned ${workoutCaloriesBurned.value} calories, and worked out for ${Number((workoutTime.value / 60).toFixed(2))} minutes 🔥`, 'green')
  }
  catch (error) {
    elementsStore.HideLoadingOverlay()
    if (error instanceof AxiosError) {
      if (error.response) {
        if (error.response.status === 400 && error.response.data.message) {
          elementsStore.ShowOverlay(error.response.data.message, 'red')
        } else {
          elementsStore.ShowOverlay('Oops! something went wrong. Try again later', 'red')
        }
      }
      else if (!error.response && (error.code === 'ECONNABORTED' || !navigator.onLine)) {
        elementsStore.ShowOverlay('A network error occurred! Please check you internet connection', 'red')
      }
      else {
        elementsStore.ShowOverlay('An unexpected error occurred!', 'red')
      }
    }
  }
}

const registerUser = async () => {
  const formData = new FormData()
  formData.append('dataObj', JSON.stringify(form.value))
  formData.append('userImage', userImage.value || '')
  if (form.value.password !== form.value.password_confirmation){
    elementsStore.ShowOverlay('Passwords do not match', 'red')
    return;
  }
  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('register', formData)
    await userAuthStore.userLogin(form.value.username, form.value.password)
    await userAuthStore.getUserData()
    await userAuthStore.getWorkoutData()
    resetForm()
    userImage.value = null
    closeOverlay('UserRegistrationOverlay')    
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay('Registration complete!', 'green')
  }
  catch (error) {
    elementsStore.HideLoadingOverlay()
    if (error instanceof AxiosError) {
      if (error.response) {
        if (error.response.status === 400 && error.response.data.message) {
          elementsStore.ShowOverlay(error.response.data.message, 'red')
        } else {
          elementsStore.ShowOverlay('Oops! something went wrong. Try again later', 'red')
        }
      }
      else if (!error.response && (error.code === 'ECONNABORTED' || !navigator.onLine)) {
        elementsStore.ShowOverlay('A network error occurred! Please check you internet connection', 'red')
      }
      else {
        elementsStore.ShowOverlay('An unexpected error occurred!', 'red')
      }
    }
  }
}

const loginUser = async () => {
  elementsStore.ShowLoadingOverlay()
  try {
    await userAuthStore.userLogin(form.value.username, form.value.password)
    await userAuthStore.getUserData()
    await userAuthStore.getWorkoutData()
    resetForm()
    closeOverlay('UserLoginOverlay')    
    elementsStore.HideLoadingOverlay()
  }
  catch (error) {
    elementsStore.HideLoadingOverlay()
    if (error instanceof AxiosError) {
      if (error.response) {
        if (error.response.status === 400 && error.response.data.message) {
          elementsStore.ShowOverlay(error.response.data.message, 'red')
        } else {
          elementsStore.ShowOverlay('Oops! something went wrong. Try again later', 'red')
        }
      }
      else if (!error.response && (error.code === 'ECONNABORTED' || !navigator.onLine)) {
        elementsStore.ShowOverlay('A network error occurred! Please check you internet connection', 'red')
      }
      else {
        elementsStore.ShowOverlay('An unexpected error occurred!', 'red')
      }
    }
  }
}

// const channel = pusher.subscribe(`customer_order_channel${userAuthStore.businessInfo?.['id']}`)
// channel.bind('complete_order', (data: {id: number, status: string})=>{
//   const orderItem = userAuthStore.customerData.orders.find(order => order.id === data.id)
//   if (orderItem){
//     orderItem.status = data.status
//   }
// })

// pusher.connection.bind('connected', () => {
//   if (userAuthStore.fetchedDataLoaded){
//     fetMissedOrders()
//   }
// })

// const fetMissedOrders = async () => {
//   const formData = new FormData()
//   formData.append('type', 'fetchMissedOrders')
//   try {
//     const response = await axiosInstance.post('customer/data', formData)
//     const data:Order[] = response.data
//     data.forEach(order=>{
//       const existingOrder = userAuthStore.customerData.orders.find(item => item.id === order.id)
//       if (existingOrder){
//         Object.assign(existingOrder, order)
//       }
//       else {
//         userAuthStore.customerData.orders.unshift(order)
//       }
//     })
//   }
//   catch {
//   }
// }


// const cancelOrder = async () => {
//   elementsStore.ShowLoadingOverlay()
//   const formData = new FormData()
//   formData.append('type', 'cancelOrder')
//   formData.append('orderId', itemPropertiesData.value?.id.toString() || '')
//   formData.append('feedback', orderItemFeedback.value)
  
//   try {
//     await axiosInstance.post('customer/data', formData)
//     const orderItem = userAuthStore.customerData.orders.find(item=> item.id === itemPropertiesData.value?.id)
//     if (orderItem){
//       orderItem.order_items.forEach(item=>{
//         if (item.manufactured_product){
//           const productItem = userAuthStore.businessProducts.find(product=> product.id === item.manufactured_product?.id && product.is_manufactured)
//           if (productItem){
//             productItem.stock_quantity += Number(item.quantity)
//           }
//         }
//         else if (item.resale_product){
//           const productItem = userAuthStore.businessProducts.find(product=> product.id === item.manufactured_product?.id && !product.is_manufactured)
//           if (productItem){
//             productItem.stock_quantity += Number(item.quantity)
//           }
//         }
//       })
//       orderItem.status = 'cancelled'
//       orderItemFeedback.value? orderItem.feedback = orderItemFeedback.value : null
//     }
//     closeOverlay('CustomerMyOrdersCancelFeedbackOverlay')
//     elementsStore.HideLoadingOverlay()
//     elementsStore.ShowOverlay('Order successfully cancelled', 'green')
//   }
//   catch (error) {
//     elementsStore.HideLoadingOverlay()
//     if (error instanceof AxiosError) {
//       if (error.response) {
//         if (error.response.status === 400 && error.response.data.message) {
//           elementsStore.ShowOverlay(error.response.data.message, 'red')
//         } else {
//           elementsStore.ShowOverlay('Oops! something went wrong. Try again later', 'red')
//         }
//       }
//       else if (!error.response && (error.code === 'ECONNABORTED' || !navigator.onLine)) {
//         elementsStore.ShowOverlay('A network error occurred! Please check you internet connection', 'red')
//       }
//       else {
//         elementsStore.ShowOverlay('An unexpected error occurred!', 'red')
//       }
//     }
//   }
// }

const isRegistrationFormValid = computed(()=>{
  return !(form.value.first_name && form.value.last_name && form.value.username && form.value.email && form.value.gender && form.value.age && form.value.country && form.value.city && form.value.password && form.value.password_confirmation)
})

const showRegistrationLoginOverlay = (overlay:string) => {
  if (overlay === 'signup'){
    closeOverlay('UserLoginOverlay')
    showOverlay('UserRegistrationOverlay')
  }
  else if (overlay === 'login'){
    closeOverlay('UserRegistrationOverlay')
    showOverlay('UserLoginOverlay')
  }
}

const showOverlay = (element: string, workout_type_item: WorkoutType | null=null) => {
  workoutTypeItem.value = workout_type_item
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'flex'
  }
}

const closeOverlay = (element: string) => {
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'none'
  }
}


</script>

<template>
  <div class="content-wrapper" v-show="elementsStore.activePage === 'MyWorkouts'" :class="{ 'is-active-page': elementsStore.activePage === `MyWorkouts` }">
    
    <div id="UserSelfieOverlay" class="overlay">
      <div class="overlay-card">
        <div class="overlay-card-content-container">
          <input ref="fileInput" type="file" accept="image/*" capture="user" style="display: none" @change="handleSelfie"/>
          <v-img class="rounded-lg" v-if="previewUrl" :src="previewUrl" cover />
        </div>
        <div class="overlay-card-action-btn-container">
          <v-btn variant="flat" size="small" color="blue" @click="retakeSelfie">Retake</v-btn>
          <v-btn class="ml-5" v-if="capturedFile" variant="flat" size="small" color="green" @click="submitWorkout">Confirm</v-btn>
          <v-btn class="ml-5" @click="elementsStore.ShowDeletionOverlay(()=> cancelWorkout(), 'Are you sure you want to cancel this workout? Your progress will be lost')" :ripple="false" variant="flat" color="red" size="small" prepend-icon="mdi-close">Cancel Workout</v-btn>
        </div>
      </div>
    </div>

    <!-- Start workout Overlay -->
    <div id="StartWorkoutOverlay" class="overlay flex-all-c bg-white">
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="white">{{ workoutTypeItem?.name.toUpperCase() }}</v-chip>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="blue">Starting workout in {{ workoutCounter }} seconds</v-chip>
      <div class="flex-all" style="width: max-content">
        <v-btn @click="skipWorkoutCounter()" :ripple="false" variant="flat" type="submit" color="blue" size="small" prepend-icon="mdi-skip-next">skip</v-btn>
        <v-btn class="ml-5" @click="stopWorkout()" :ripple="false" variant="flat" type="submit" color="red" size="small" prepend-icon="mdi-close">stop</v-btn>
      </div>
    </div>

    <!-- working out Overlay -->
    <div id="WorkingOutOverlay" class="overlay flex-all-c bg-white" style="background-color: white">
      <video :src="workoutTypeItem?.animation" ref="workoutTypeItemVidoes" autoplay muted loop style="width: 90%; max-width: 500px; max-height: 200px; border-radius: 8px;"></video>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="white">{{ workoutTypeItem?.name.toUpperCase() }}</v-chip>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="blue"><v-icon icon="mdi-timer" size="large" />: {{ formatTimeInHHMMSS(workoutTime) }}</v-chip>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="blue"><v-icon icon="mdi-star-circle" size="large" />: {{ workoutPointsEarned }}</v-chip>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="blue"><v-icon icon="mdi-fire" size="large" />: {{ workoutCaloriesBurned }}</v-chip>
      <div class="flex-all" style="width: max-content">
        <v-btn @click="openCamera()" :ripple="false" variant="flat" type="submit" color="green" size="small" prepend-icon="mdi-check-circle">Finish Workout</v-btn>
        <v-btn class="ml-5" v-if="workoutTimer" @click="pauseWorkout()" :ripple="false" variant="flat" color="yellow" size="small" prepend-icon="mdi-pause-circle">Rest</v-btn>
        <v-btn class="ml-5" v-if="!workoutTimer" @click="startWorkoutTimer()" :ripple="false" variant="flat" color="blue" size="small" prepend-icon="mdi-play-circle">Resume</v-btn>
        <v-btn class="ml-5" @click="elementsStore.ShowDeletionOverlay(()=> cancelWorkout(), 'Are you sure you want to cancel this workout? Your progress will be lost')" :ripple="false" variant="flat" color="red" size="small" prepend-icon="mdi-close">Cancel Workout</v-btn>
      </div>
    </div>

    <!-- User login Overlay -->
    <div id="UserLoginOverlay" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay('UserLoginOverlay')" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
        <div class="overlay-card-info-container">
          <v-chip :size="elementsStore.btnSize2" color="red">
            Don't have an account yet?<a @click="showRegistrationLoginOverlay('signup')" class="signup-login-link">Sign Up</a>
          </v-chip>
        </div>
        <div class="overlay-card-content-container">
          <v-text-field class="input-field" v-model="form.username" label="USERNAME" hint="Enter your username" density="comfortable" type="text" clearable
            persistent-hint prepend-inner-icon="mdi-account">
          </v-text-field>
          <v-text-field class="input-field"
            :append-inner-icon="passwordVisibility ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"
            @click:append-inner="passwordVisibility = !passwordVisibility" :type="passwordVisibility ? 'text' : 'password'"
            clearable density="comfortable" v-model="form.password" label="PASSWORD" hint="Enter your password"
            prepend-inner-icon="mdi-lock-outline"  persistent-hint
          />
        </div>
        <div class="overlay-card-action-btn-container">
          <v-btn @click="loginUser()" :disabled="!(form.username && form.password)" :ripple="false" variant="flat" type="submit" color="black" size="small" append-icon="mdi-checkbox-marked-circle">SUBMIT</v-btn>
        </div>
      </div>
    </div>

    <!-- User Registration Overlay -->
    <div id="UserRegistrationOverlay" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay('UserRegistrationOverlay')" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
        <div class="overlay-card-info-container">
          <v-chip :size="elementsStore.btnSize2" color="red">NB: Fields with [*] are mandatory.</v-chip>
          <v-chip :size="elementsStore.btnSize2" color="red">
            Already have an account?<a @click="showRegistrationLoginOverlay('login')" class="signup-login-link">Login</a>
          </v-chip>
        </div>
        <div class="overlay-card-content-container">
          <v-text-field class="input-field" v-model="form.first_name" label="FIRST NAME [*]" hint="Enter your first name" density="comfortable" type="text" clearable persistent-hint prepend-inner-icon="mdi-account" />
          <v-text-field class="input-field" v-model="form.last_name" label="LAST NAME [*]" hint="Enter your last name" density="comfortable" type="text" clearable persistent-hint prepend-inner-icon="mdi-account" />
          <v-text-field class="input-field" v-model="form.username" label="USERNAME [*]" hint="Enter a username" density="comfortable" type="text" clearable persistent-hint prepend-inner-icon="mdi-account" />
          <v-text-field class="input-field" v-model="form.email" label="EMAIL [*]" hint="Enter a valid email" density="comfortable" type="email" clearable persistent-hint prepend-inner-icon="mdi-email" />
          <v-select class="input-field" v-model="form.gender" label="GENDER [*]" :items="['Male', 'Female', 'Other']" hint="Select your gender" density="comfortable" clearable persistent-hint prepend-inner-icon="mdi-gender-male-female" />
          <v-text-field class="input-field" v-model="form.age" label="AGE [*]" hint="Enter your age in years" density="comfortable" type="number" clearable persistent-hint prepend-inner-icon="mdi-calendar" />
          <v-select class="select" :items="countriesData.sort((a, b) => a.name.localeCompare(b.name)).map(item=> item.name)" label="COUNTRY [*]" v-model="form.country"
            clearable variant="solo-filled" density="comfortable" persistent-hint hint="Select the country you live in" prepend-inner-icon="mdi-earth">
          </v-select>
          <v-text-field class="input-field" v-model="form.city" label="CITY [*]" hint="Enter your city" density="comfortable" type="text" clearable persistent-hint prepend-inner-icon="mdi-city" />
          <v-text-field class="input-field" :append-inner-icon="passwordVisibility ? 'mdi-eye-off-outline' : 'mdi-eye-outline'" @click:append-inner="passwordVisibility = !passwordVisibility" :type="passwordVisibility ? 'text' : 'password'"
            clearable density="comfortable" v-model="form.password" label="PASSWORD [*]" hint="Enter a password"
            prepend-inner-icon="mdi-lock-outline">
          </v-text-field>
          <v-text-field class="input-field" :append-inner-icon="passwordVisibility ? 'mdi-eye-off-outline' : 'mdi-eye-outline'"  @click:append-inner="passwordVisibility = !passwordVisibility"
            :type="passwordVisibility ? 'text' : 'password'" clearable density="comfortable" v-model="form.password_confirmation"
            label="REPEAT PASSWORD [*]" hint="Repeat the password" prepend-inner-icon="mdi-lock-outline">
          </v-text-field>
          <v-text-field class="input-field" v-model="form.height" label="HEIGHT (CM)" hint="Your height in centimeters" density="comfortable" type="number" clearable persistent-hint prepend-inner-icon="mdi-ruler" />
          <v-text-field class="input-field" v-model="form.weight" label="WEIGHT (KG)" hint="Your weight in kilograms" density="comfortable" type="number" clearable persistent-hint prepend-inner-icon="mdi-scale-bathroom" />
          <v-textarea class="input-field" v-model="form.bio" label="BIO" hint="Write a short bio" density="comfortable" rows="3" auto-grow clearable persistent-hint prepend-inner-icon="mdi-text" />
          <v-file-input class="input-field" v-model="userImage" label="PROFILE IMAGE" hint="Upload your image" density="comfortable" accept="image/*" clearable persistent-hint prepend-icon="mdi-camera" />
        </div>
        <div class="overlay-card-action-btn-container">
          <v-btn @click="registerUser()" :disabled="isRegistrationFormValid" :ripple="false" variant="flat" type="submit" color="black" size="small" append-icon="mdi-checkbox-marked-circle">SUBMIT</v-btn>
        </div>
      </div>
    </div>

    <TheLoader v-if="!workoutTypes" :func="userAuthStore.getAppData" />
    <NoData v-if="workoutTypes && workoutTypes.length === 0" />
    <div class="items-container" v-if="workoutTypes && workoutTypes.length > 0">
      <v-container>
      <v-row dense>
        <v-col v-for="_item_ in workoutTypes" :key="_item_.id" cols="12" sm="6" md="4" lg="3">
          <v-card class="workout-card" elevation="3" rounded="lg">
            <v-card-title class="text-h6 font-weight-bold">{{ _item_.name.toUpperCase() }}</v-card-title>
            <v-card-text class="text-body-2">{{ _item_.description }}</v-card-text>
            <v-img :src="_item_.thumbnail" height="200" cover ></v-img>
            <v-card-actions>
              <v-btn @click="startWorkout(_item_)" color="primary" variant="tonal" block>Start Workout</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    </div>
  </div>
</template>

<style scoped>

.overlay-card {
  max-width: 600px !important;
}
.view-card-1{
  max-width: 1300px !important;
}
.view-card-2{
  max-width: 1150px !important;
}
.view-card-3{
  max-width: 800px !important;
}
.items-container{
  width: 100% !important;
  height: 100% !important;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  align-items: flex-start;
}
.workout-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.signup-login-link {
  color: #007bff !important;
  font-weight: bold !important;
  text-decoration: none !important;
  margin-left: 5px !important;
}

.signup-login-link:hover {
  text-decoration: underline !important;
  cursor: pointer !important;
}

</style>
