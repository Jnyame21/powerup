<script setup lang="ts">
import { useElementsStore } from '@/stores/elementsStore';
import { useUserAuthStore } from '@/stores/userAuthStore';


const elementsStore = useElementsStore()
const userAuthStore = useUserAuthStore()

const changePage = (page_name: any) => {
  elementsStore.activePage = page_name
  localStorage.setItem('activePage', page_name)
}


</script>


<template>
  <div class="nav-container">
    <v-list class="nav-list-container">
      <v-list-item @click="changePage('MyWorkouts')" class="nav-item nav-link" prepend-icon="mdi-shopping">
        WORKOUTS
      </v-list-item>
      <v-list-item v-if="userAuthStore.isAuthenticated" @click="changePage('CustomerMyOrders')" class="nav-item nav-link" prepend-icon="mdi-package-variant">
        MY ORDERS
      </v-list-item>
    </v-list>
  </div>
</template>


<style scoped>

</style>
