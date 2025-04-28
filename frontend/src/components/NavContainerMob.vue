<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()


const changePage = (page_name: any) => {
  elementsStore.activePage = page_name
  localStorage.setItem('activePage', page_name)
}


const showOverlay = (element:string) => {
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'flex'
  }
}


</script>


<template>
  <div class="nav-container-drawer" v-show="elementsStore.navDrawer">
    <v-list class="nav-list-container">
      <v-list-item @click="changePage('MyWorkouts')" class="nav-item nav-link" prepend-icon="mdi-shopping">
        WORKOUTS
      </v-list-item>
      <div class="flex-all mt-15" v-if="userAuthStore.isAuthenticated">
        <v-btn @click="showOverlay('LogoutOverlay')" color="red" size="small" prepend-icon="mdi-logout">LOGOUT</v-btn>
      </div>
    </v-list>
  </div>
</template>


<style scoped>

</style>
