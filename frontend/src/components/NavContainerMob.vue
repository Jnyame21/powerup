<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import axiosInstance from '@/utils/axiosInstance';
import { AxiosError } from 'axios';

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

const deleteCommunity = async (item_id: number) => {
  const formData = new FormData()
  formData.append('type', 'deleteCommunity')
  formData.append('itemId', item_id.toString())
  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('workout/data', formData)
    const itemToDelete = userAuthStore.communitiesData.find(item=> item.id === item_id)
    if (itemToDelete) {
      userAuthStore.communitiesData.splice(userAuthStore.communitiesData.indexOf(itemToDelete), 1)
    }
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


</script>


<template>
  <div class="nav-container-drawer" v-show="elementsStore.navDrawer">
    <v-list class="nav-list-container">
      <v-list-item @click="changePage('MyWorkouts')" class="nav-item nav-link" prepend-icon="mdi-run">
        WORKOUTS
      </v-list-item>

      <v-list-item v-if="userAuthStore.isAuthenticated" @click="changePage('TodayWorkouts')" class="nav-item nav-link" prepend-icon="mdi-calendar-today">
        TODAY
      </v-list-item>

      <v-list-item v-if="userAuthStore.isAuthenticated" @click="changePage('WeekWorkouts')" class="nav-item nav-link" prepend-icon="mdi-calendar-week">
        THIS WEEK
      </v-list-item>

      <v-list-item v-if="userAuthStore.isAuthenticated" @click="changePage('MonthWorkouts')" class="nav-item nav-link" prepend-icon="mdi-calendar-month">
        THIS MONTH
      </v-list-item>

      <v-list-group v-if="userAuthStore.isAuthenticated">
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" class="nav-item" prepend-icon="mdi-account-group">
            COMMUNITIES
          </v-list-item>
        </template>
        <v-list-item class="nav-link" style="color: blue; font-size: .7rem; font-family: Verdana, Geneva, Tahoma, sans-serif;" @click="showOverlay('CreateCommunityOverlay')">
          ADD COMMUNITY
        </v-list-item>
        <v-list-item class="nav-link" style="color: blue; font-size: .7rem; font-family: Verdana, Geneva, Tahoma, sans-serif;" @click="showOverlay('JoinCommunityOverlay')">
          JOIN COMMUNITY
        </v-list-item>
        <h4 v-for="community in userAuthStore.communitiesData" :key="community.id" class="nav-title d-flex align-center justify-space-between">
          <span class="nav-link" @click="changePage(`MyCommunity,${community.id}`)">{{ community.name }}</span>
          <v-icon v-if="elementsStore.activePage !== `MyCommunity,${community.id}` && community.admins.find(item=> item.username === userAuthStore.userData?.username)" icon="mdi-delete" class="me-2" color="red" @click.stop="elementsStore.ShowDeletionOverlay(()=> deleteCommunity(community.id), 'Are you sure you want to delete this community?. All data including challenges for this community will be lost.')"/>
        </h4>
      </v-list-group>

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
