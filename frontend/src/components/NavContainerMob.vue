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
      <v-list-group v-if="userAuthStore.isAuthenticated">
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-clipboard-text" class="nav-item">
            HISTORY
          </v-list-item>
        </template>
        <v-list-group v-for="(month, index) in userAuthStore.filteredWorkoutData" :key="index">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" class="nav-item">
              {{ month.month }}
            </v-list-item>
          </template>
          <v-list-item class="nav-title nav-link" @click="changePage(`MyWorkoutStatsMonth,${month.month}`)">
            {{ month.month }}
          </v-list-item>
          <v-list-group v-for="(week, weekIndex) in month.weeks" :key="weekIndex">
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" class="nav-item">
                {{ week.week }}
              </v-list-item>
            </template>
            <h4 class="nav-title nav-link" @click="changePage(`MyWorkoutStatsWeek,${month.month}${week.week}`)">
              {{ week.week }}
            </h4>
            <h4 class="nav-title nav-link" v-for="(day, dayIndex) in week.days" :key="dayIndex" @click="changePage(`MyWorkoutStatsDay,${month.month}${week.week}${day.day}`)">
              {{ day.day }}
            </h4>
          </v-list-group>
        </v-list-group>
      </v-list-group>
      <div class="flex-all mt-15" v-if="userAuthStore.isAuthenticated">
        <v-btn @click="showOverlay('LogoutOverlay')" color="red" size="small" prepend-icon="mdi-logout">LOGOUT</v-btn>
      </div>
    </v-list>
  </div>
</template>


<style scoped>

</style>
