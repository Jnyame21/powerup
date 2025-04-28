<script setup lang="ts">
import { computed, ref} from 'vue';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import { formatDate } from '@/utils/util';
import type { WorkoutType } from '@/utils/types_utils';
import TheLoader from '@/components/TheLoader.vue';
import NoData from '@/components/NoData.vue';
import pusher from '@/utils/pusher';
import axiosInstance from '@/utils/axiosInstance';
import { AxiosError } from 'axios';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()


const workoutTypes = computed(()=>{
    return userAuthStore.workoutTypes
})

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

const showOverlay = (element: string) => {
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

    <TheLoader v-if="!userAuthStore.fetchedDataLoaded" :func="userAuthStore.getAppData" />
    <div class="content-header" v-if="userAuthStore.fetchedDataLoaded"></div>
    <div class="content-header" v-if="userAuthStore.fetchedDataLoaded"></div>
    <NoData v-if="userAuthStore.fetchedDataLoaded && workoutTypes.length === 0" />
    <v-container v-if="userAuthStore.fetchedDataLoaded && workoutTypes.length > 0">
    <v-row dense>
      <v-col v-for="workout in workoutTypes" :key="workout.id" cols="12" sm="6" md="4" lg="3">
        <v-card class="workout-card" elevation="3" rounded="lg">
          <v-img
            :src="workout.thumbnail"
            height="200"
            cover
          ></v-img>

          <v-card-title class="text-h6 font-weight-bold">
            {{ workout.name }}
          </v-card-title>

          <v-card-text class="text-body-2">
            {{ workout.description }}
          </v-card-text>

          <v-responsive aspect-ratio="16/9" v-if="workout.animation">
            <video
              :src="workout.animation"
              controls
              autoplay
              muted
              loop
              style="width: 100%; border-radius: 8px;"
            ></video>
          </v-responsive>

          <v-card-actions>
            <v-btn color="primary" variant="tonal" block>
              Start Workout
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
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

</style>
