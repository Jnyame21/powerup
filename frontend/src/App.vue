<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onBeforeMount } from 'vue';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import TheLoader from '@/components/TheLoader.vue';
import { defaultAxiosInstance } from '@/utils/axiosInstance';

const elementsStore = useElementsStore()
const userAuthStore = useUserAuthStore()

onBeforeMount(()=>{
  document.body.style.overflow = 'hidden'
  refreshServer()
  setInterval(refreshServer, 60000)
})

if (window.innerWidth >= 767 && window.innerWidth < 2000) {
  elementsStore.btnSize1 = 'small'
  elementsStore.btnSize2 = 'default'
}
else if (window.innerWidth >= 2000) {
  elementsStore.btnSize1 = 'default'
  elementsStore.btnSize2 = 'large'
}
if (window.innerWidth > 1000) {
  elementsStore.onDesk = true
}

window.addEventListener('resize', () => {
  if (window.innerWidth <= 1000) {
    elementsStore.onDesk = false
  }
  else if (window.innerWidth > 1000) {
    elementsStore.onDesk = true
  }
  if (window.innerWidth < 767) {
    elementsStore.btnSize1 = 'x-small'
    elementsStore.btnSize2 = 'small'
  }
  else if (window.innerWidth >= 767 && window.innerWidth < 2000) {
    elementsStore.btnSize1 = 'small'
    elementsStore.btnSize2 = 'default'
  }
  else if (window.innerWidth >= 2000) {
    elementsStore.btnSize1 = 'default'
    elementsStore.btnSize2 = 'large'
  }
})

const refreshServer = async()=>{
  try {
    defaultAxiosInstance.post('refresh_server')
  }
  catch {
    Promise.reject()
  }
}

const reloadPage = ()=>{
  window.location.reload()
}

const closeOverlay = (element: string)=>{
  elementsStore.deleteOverlayMessage = ''
  const overlay = document.getElementById(element)
  if (overlay){
    overlay.style.display = 'none'
  }
}

const logout = async ()=>{
  closeOverlay('LogoutOverlay')
  userAuthStore.logoutUser()
}

const continueDeletion = ()=>{
  closeOverlay('deleteOverlay')
  elementsStore.deleteFunction()
}


</script>

<template>
  <v-app style="overflow: hidden">
    <div class="container" style="background-color: white">
    <!-- Logout Overlay -->
      <div id="LogoutOverlay" class="overlay">
        <v-card class="overlay-card">
          <v-card-text >
            <p class="overlay-text" v-if="userAuthStore.userData">Are you sure you want to logout?</p>
          </v-card-text>
          <v-card-actions>
            <v-btn class="mr-5" size="small" color="red" @click="logout">YES</v-btn>
            <v-btn color="black" size="small" class="ml-5" @click="closeOverlay('LogoutOverlay')">NO</v-btn>
          </v-card-actions>
        </v-card>
      </div>

      <!-- Session Overlay -->
      <div id="AlertOverlay" class="overlay">
        <v-card class="overlay-card">
          <v-card-text>
            <p class="overlay-text" :style="`color: ${elementsStore.overlayMessageColor}`">{{elementsStore.overlayMessage}}</p>
          </v-card-text>
          <v-card-actions class="flex-all">
            <v-btn @click="closeOverlay('AlertOverlay')" color="black" variant="flat">OK</v-btn>
          </v-card-actions>
        </v-card>
      </div>

      <!-- Delete Overlay -->
      <div id="deleteOverlay" class="overlay">
        <v-card class="overlay-card">
          <v-card-text>
            <p class="overlay-text" >{{ elementsStore.deleteOverlayMessage }}</p>
          </v-card-text>
          <v-card-actions>
            <v-btn class="mr-5" color="red" size="small" variant="flat" @click="continueDeletion">YES</v-btn>
            <v-btn class="ml-5" color="black" size="small" variant="flat" @click="closeOverlay('deleteOverlay')">NO</v-btn>
          </v-card-actions>
        </v-card>
      </div>

      <!-- Loading Overlay -->
      <div id="LoadingOverlay" class="overlay">
        <v-progress-circular :size="50" :width="10" indeterminate color="blue" />
      </div>

      <RouterView/>
      <TheLoader :func="reloadPage" v-if="!userAuthStore.userData && !userAuthStore.workoutTypes"/>
    </div>
    </v-app>
</template>

<style scoped>

div:hover{
  cursor: default;
}
.overlay-card{
  max-width: 95% !important;
  width: fit-content !important;
}
.overlay-text{
  margin-top: 1em;
  margin-bottom: 1em;
  font-weight: bold;
  text-align: center;
  font-family: Verdana, Geneva, Tahoma, sans-serif;
  font-size: .8rem;
}
#session-alert{
  z-index: 1000 !important;
}

#LoadingOverlay{
  z-index: 1000 !important;
}

</style>
