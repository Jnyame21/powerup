<script setup lang="ts">
import { computed, ref} from 'vue';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import { formatTimeInHHMMSS, countriesData } from '@/utils/util';
import type { WorkoutType, Workout } from '@/utils/types_utils';
import TheLoader from '@/components/TheLoader.vue';
import NoData from '@/components/NoData.vue';
import pusher from '@/utils/pusher';
import axiosInstance from '@/utils/axiosInstance';
import { AxiosError } from 'axios';
import type { VNodeRef } from 'vue';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()
const workoutCounter = ref(15)
const workoutTime = ref(0);
const workoutTypeItem = ref<WorkoutType | null>(null)
const workoutTypeItemVidoes = ref<HTMLVideoElement | null>(null)
const passwordVisibility = ref(false)
const userImage = ref<File | null>(null)
const selfieUrl = ref('')
const video = ref<VNodeRef | null>(null)
const canvas = ref<VNodeRef | null>(null)
const form = ref({
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
  form.value = { email: '', gender: '', age: null, height: null, weight: null, country: '', city: '', bio: '', password: '', password_confirmation: '', username: '' }
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
  stopCamera()
  clearInterval(workoutTimer.value);
  workoutTimer.value = undefined
  workoutTime.value = 0;
  workoutTypeItem.value = null;
  selfieUrl.value = '';
  video.value = null;
  canvas.value = null;
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
  const constraint = {
    video: {
      facingMode: 'user',
    },
    audio: false
  }
  elementsStore.ShowLoadingOverlay()
  navigator.mediaDevices.getUserMedia(constraint).then((stream)=>{
    video.value.srcObject = stream
    closeOverlay('WorkingOutOverlay')
    showOverlay('UserSelfieOverlay', workoutTypeItem.value)
    elementsStore.HideLoadingOverlay()
  })
  .catch(()=>{
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay('Could not access camera. Please allow camera permissions.', 'red')
  })
};

const takeSelfie = () => {
  const ctx = canvas.value.getContext('2d');
  canvas.value.width = video.value.videoWidth;
  canvas.value.height = video.value.videoHeight;
  ctx.drawImage(video.value, 0, 0);
  selfieUrl.value = canvas.value.toDataURL('image/png');
};

const retakeSelfie = () => {
  canvas.value = null
  selfieUrl.value = ''
};

const stopCamera = () => {
  const stream = video.value?.srcObject as MediaStream | null;
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    video.value.srcObject = null;
  }
};

const submitWorkout = async () => {
  elementsStore.ShowLoadingOverlay()
  const res = await fetch(selfieUrl.value);
  const selfieBlob = await res.blob();
  const selfieFile = new File([selfieBlob], `${new Date().getTime()}_selfie.png`, { type: selfieBlob.type });
  
  const formData = new FormData()
  formData.append('type', 'createWorkout')
  formData.append('workoutType', workoutTypeItem.value?.id.toString() || '')
  formData.append('duration', workoutTime.value.toString())
  formData.append('pointsEarned', workoutPointsEarned.value.toString())
  formData.append('caloriesBurned', workoutCaloriesBurned.value.toString())
  formData.append('selfie', selfieFile || '')
  
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const data: Workout = response.data
    userAuthStore.workoutData.unshift(data)
    stopCamera()
    selfieUrl.value = ''
    video.value =  null
    canvas.value = null
    closeOverlay('UserSelfieOverlay')    
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay(`Awesome job! 🌟 You pushed through ${Number((workoutTime.value / 60).toFixed(2))} minutes ⏱, burned ${workoutCaloriesBurned.value} calories 🔥, and earned ${workoutPointsEarned.value} points 🏆. You're unstoppable! 🚀`, 'green')
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
  if (form.value.age && form.value.age < 9){
    elementsStore.ShowOverlay('You must be at least ten(10) years of age to use this platform', 'red')
    return;
  }
  if (form.value.height && form.value.height <= 0){
    elementsStore.ShowOverlay("The height must be greater than zero. Leave it blank if you don't know your height", 'red')
    return;
  }
  if (form.value.weight && form.value.weight <= 0){
    elementsStore.ShowOverlay("The weight must be greater than zero. Leave it blank if you don't know your weight", 'red')
    return;
  }
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
        }
        else if (error.response.status === 401){
          elementsStore.ShowOverlay("No account found with the given credentials. Sign up if you don't have an account", 'red')
        }
        else {
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

const isRegistrationFormValid = computed(()=>{
  return !(form.value.username && form.value.email && form.value.gender && form.value.age && form.value.country && form.value.city && form.value.password && form.value.password_confirmation)
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
  <div id="MyWorkouts" class="content-wrapper" v-show="elementsStore.activePage === 'MyWorkouts'" :class="{ 'is-active-page': elementsStore.activePage === `MyWorkouts` }">

    <!-- User selfie Overlay -->
    <div id="UserSelfieOverlay" class="overlay">
      <div class="overlay-card">
        <div class="overlay-card-content-container">
          <video v-show="!selfieUrl" ref="video" autoplay playsinline class="video"></video>
          <canvas ref="canvas" style="display: none;"></canvas>
          <v-img class="rounded-lg selfie" v-show="selfieUrl" :src="selfieUrl" cover />
        </div>
        <div class="overlay-card-action-btn-container">
          <v-btn v-show="!selfieUrl" variant="flat" size="small" prepend-icon="mdi-camera" color="blue" @click="takeSelfie">take selfie</v-btn>
          <v-btn v-show="selfieUrl" variant="flat" size="small" color="blue" @click="retakeSelfie">Retake</v-btn>
          <v-btn class="ml-5" v-show="selfieUrl" variant="flat" size="small" color="green" @click="submitWorkout">Confirm</v-btn>
          <v-btn class="ml-5" @click="elementsStore.ShowDeletionOverlay(()=> cancelWorkout(), 'Are you sure you want to cancel this workout? Your progress will be lost')" :ripple="false" variant="flat" color="red" size="small" prepend-icon="mdi-close">Cancel</v-btn>
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
      <v-chip class="mb-2 mt-5" :size="elementsStore.btnSize2" color="red">{{ workoutTypeItem?.name.toUpperCase() }}</v-chip>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="blue"><v-icon icon="mdi-timer" size="large" />: {{ formatTimeInHHMMSS(workoutTime) }}</v-chip>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="blue"><v-icon icon="mdi-star-circle" size="large" />: {{ workoutPointsEarned }}</v-chip>
      <v-chip class="mb-2" :size="elementsStore.btnSize2" color="blue"><v-icon icon="mdi-fire" size="large" />: {{ workoutCaloriesBurned }}</v-chip>
      <div class="flex-all" style="width: max-content">
        <v-btn @click="openCamera()" :ripple="false" variant="flat" type="submit" color="green" size="small" prepend-icon="mdi-check-circle">Done</v-btn>
        <v-btn class="ml-3" v-if="workoutTimer" @click="pauseWorkout()" :ripple="false" variant="flat" color="yellow" size="small" prepend-icon="mdi-pause-circle">Rest</v-btn>
        <v-btn class="ml-3" v-if="!workoutTimer" @click="startWorkoutTimer()" :ripple="false" variant="flat" color="blue" size="small" prepend-icon="mdi-play-circle">Resume</v-btn>
        <v-btn class="ml-3" @click="elementsStore.ShowDeletionOverlay(()=> cancelWorkout(), 'Are you sure you want to cancel this workout? Your progress will be lost')" :ripple="false" variant="flat" color="red" size="small" prepend-icon="mdi-close">Cancel</v-btn>
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
          <v-text-field class="input-field" v-model="form.username" label="USERNAME [*]" hint="Enter a username" density="comfortable" type="text" clearable persistent-hint prepend-inner-icon="mdi-account" />
          <v-text-field class="input-field" v-model="form.email" label="EMAIL [*]" hint="Enter a valid email address" density="comfortable" type="email" clearable persistent-hint prepend-inner-icon="mdi-email" />
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
        <v-col v-for="_item_ in workoutTypes" :key="_item_.id" cols="12" xs="12" sm="6" md="6" lg="4" >
          <v-card class="workout-card" elevation="1" rounded="lg">
            <v-card-title class="text-h6 font-weight-bold text-wrap"  style="word-wrap: break-word;">{{ _item_.name.toUpperCase() }}</v-card-title>
            <v-card-text class="workout-description">{{ _item_.description }}</v-card-text>
            <v-img :src="_item_.thumbnail" height="200" cover ></v-img>
            <v-card-actions>
              <v-btn @click="startWorkout(_item_)" :ripple="false" variant="flat" color="blue" size="small" prepend-icon="mdi-lightning-bolt" block>Start Workout</v-btn>
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
.workout-description{
  font-size: .85rem !important;
  font-family: Verdana, Geneva, Tahoma, sans-serif !important;
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
.video {
  width: 100%;
  max-width: 400px;
  border: 1px solid #ccc;
  margin: auto;
}
.selfie {
  width: 100%;
  max-width: 400px;
  margin-top: 10px;
  border: 2px solid #0b7285;
  margin: auto;
}

</style>
