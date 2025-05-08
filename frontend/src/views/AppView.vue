<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore'
import { useElementsStore } from '@/stores/elementsStore'
import { useHead } from '@vueuse/head';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';
import axiosInstance from '@/utils/axiosInstance';
import type { Community } from '@/utils/types_utils';
import { AxiosError } from 'axios';
import { onMounted, watch, ref } from 'vue';
import NavContainerDesk from '@/components/NavContainerDesk.vue';
import NavContainerMob from '@/components/NavContainerMob.vue';
import MyWorkouts from '@/components/MyWorkouts.vue';
import { getCalendarData, getWeekNumberInMonth } from '@/utils/util';
import MyWorkoutStats from '@/components/MyWorkoutStats.vue';
import TodayWorkouts from '@/components/TodayWorkouts.vue';
import WeekWorkouts from '@/components/WeekWorkouts.vue';
import MonthWorkouts from '@/components/MonthWorkouts.vue';
import MyCommunity from '@/components/MyCommunity.vue';


useHead({
  meta: [
    {
      name: "description",
      content: "Stay motivated and crush your fitness goals with PowerUp. PowerUp is a community-driven workout app that helps you track activities, join challenges, and climb the leaderboards — all while staying connected with friends.",
    },
    {
      name: "robots",
      content: "index, follow"
    }
  ],
});

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()
const communityImage = ref<File | null>(null)
const communityData = ref<Community>({
  id: 0,
  name: '',
  description: '',
  img: '',
  challenges: [],
  admins: [],
  members: [],
  join_code: '',
  date: '',
})

onMounted(()=>{
  if (userAuthStore.isAuthenticated){
    elementsStore.activePage = localStorage.getItem('activePage') || 'MyWorkouts'
  }
  else {
    elementsStore.activePage = 'MyWorkouts'
  }
})

watch(()=> userAuthStore.currentYearEndDate, (newValue)=>{
  if (newValue && userAuthStore.filteredWorkoutData.length === 0){
    userAuthStore.filteredWorkoutData = getCalendarData(new Date(userAuthStore.currentYearStartDate), new Date(newValue))
  }
}, { 'immediate': true, 'deep': true })

watch(() => userAuthStore.workoutData, (newValue, oldValue) => {
  const filteredData = oldValue ? newValue.filter(item=> !oldValue.includes(item)) : newValue
  if (filteredData) {
    let date: any = null
    let dayName = ''
    let weekNumber = 0
    let monthName = ''
    newValue.forEach(item => {
      date = new Date(item.date.toString())
      dayName = date.toLocaleString('default', { 'weekday': 'long' })
      weekNumber = getWeekNumberInMonth(date)
      monthName = date.toLocaleString('default', { 'month': 'long' }).toUpperCase()
      const MonthData = userAuthStore.filteredWorkoutData.find(month => month.month.toLowerCase() === monthName.toLowerCase())
      if (MonthData) {
        MonthData.caloriesBurned += Number(item.calories_burned)
        MonthData.pointsEarned += Number(item.points)
        MonthData.duration += Number(item.duration)
        MonthData.data.unshift(item)
        const weekData = MonthData.weeks.find(week=> week.week.split(' ')[1].toString() === weekNumber.toString())
        if (weekData){
          weekData.caloriesBurned += Number(item.calories_burned)
          weekData.pointsEarned += Number(item.points)
          weekData.duration += Number(item.duration)
          weekData.data.unshift(item)
          const dayData = weekData.days.find(day=> day.day.split('(')[0].toLowerCase() === dayName.toLowerCase())
          if (dayData){
            dayData.caloriesBurned += Number(item.calories_burned)
            dayData.pointsEarned += Number(item.points)
            dayData.duration += Number(item.duration)
            dayData.data.unshift(item)
          }
        }
      }
    })     
  }
}, { 'immediate': true, 'deep': 1 })

const createCommunity = async () => {
  const formData = new FormData()
  formData.append('type', 'createCommunity')
  formData.append('dataObj', JSON.stringify(communityData.value))
  formData.append('communityImage', communityImage.value || '')
  elementsStore.ShowLoadingOverlay()
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const responseData: Community = response.data
    userAuthStore.communitiesData.unshift(responseData)
    communityData.value.name
    communityData.value.description
    communityImage.value = null
    closeOverlay('CreateCommunityOverlay')
    elementsStore.activePage = `MyCommunity,${responseData.id}`
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

const joinCommunity = async () => {
  const formData = new FormData()
  formData.append('type', 'joinCommunity')
  formData.append('dataObj', JSON.stringify(communityData.value))
  elementsStore.ShowLoadingOverlay()
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const responseData: Community = response.data
    userAuthStore.communitiesData.unshift(responseData)
    communityData.value.name
    communityData.value.description
    communityData.value.join_code = ''
    communityImage.value = null
    closeOverlay('JoinCommunityOverlay')
    elementsStore.activePage = `MyCommunity,${responseData.id}`
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

const closeOverlay = (element: string) => {
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'none'
  }
}

</script>

<template>
  <TheHeader v-if="userAuthStore.workoutTypes"/>
  <main class="main" v-if="userAuthStore.workoutTypes">
    <NavContainerMob v-if="!elementsStore.onDesk" />
    <NavContainerDesk v-if="elementsStore.onDesk" />
    <div class="pages-container">

      <!-- Join Community Overlay -->
      <div id="JoinCommunityOverlay" class="overlay">
        <div class="overlay-card">
          <v-btn @click="closeOverlay('JoinCommunityOverlay')" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
          <div class="overlay-card-info-container">
            <v-chip :size="elementsStore.btnSize2" color="red">NB: Fields with [*] are mandatory.</v-chip>
          </div>
          <div class="overlay-card-content-container">
            <v-text-field class="input-field" v-model="communityData.join_code" label="COMMUNITY CODE [*]" hint="Enter the community code" density="comfortable" type="text" clearable persistent-hint />
          </div>
          <div class="overlay-card-action-btn-container">
            <v-btn @click="joinCommunity()" :disabled="!(communityData.join_code)" :ripple="false" variant="flat" type="submit" color="black" size="small" append-icon="mdi-checkbox-marked-circle">JOIN</v-btn>
          </div>
        </div>
      </div>

      <!-- Create Community Overlay -->
      <div id="CreateCommunityOverlay" class="overlay">
        <div class="overlay-card">
          <v-btn @click="closeOverlay('CreateCommunityOverlay')" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
          <div class="overlay-card-info-container">
            <v-chip :size="elementsStore.btnSize2" color="red">NB: Fields with [*] are mandatory.</v-chip>
          </div>
          <div class="overlay-card-content-container">
            <v-text-field class="input-field" v-model="communityData.name" label="NAME [*]" hint="Enter the name of the community" density="comfortable" type="text" clearable persistent-hint />
            <v-textarea class="input-field" v-model="communityData.description" label="DESCRIPTION [*]" hint="Enter the description of the community" density="comfortable" rows="3" auto-grow clearable persistent-hint prepend-inner-icon="mdi-text" />
            <v-file-input class="input-field" v-model="communityImage" label="IMAGE" hint="Upload a profile image for the community" showSize  density="comfortable" accept="image/*" clearable persistent-hint prepend-icon="mdi-image" />
          </div>
          <div class="overlay-card-action-btn-container">
            <v-btn @click="createCommunity()" :disabled="!(communityData.name && communityData.description)" :ripple="false" variant="flat" type="submit" color="black" size="small" append-icon="mdi-checkbox-marked-circle">CREATE</v-btn>
          </div>
        </div>
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'MyWorkouts' }">
        <MyWorkouts/>
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'TodayWorkouts' }">
        <TodayWorkouts/>
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'WeekWorkouts' }">
        <WeekWorkouts/>
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'MonthWorkouts' }">
        <MonthWorkouts/>
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage.split(',')[0] === 'MyCommunity' }">
        <MyCommunity v-for="community in userAuthStore.communitiesData" :key="community.id" :id="community.id" />
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage.split(',')[0] === 'MyWorkoutStatsMonth' }">
        <MyWorkoutStats v-for="(month, index) in userAuthStore.filteredWorkoutData" :key="index" :data="month.data" :title="`${month.month}`"
          :keyValue="`${month.month}`" typeValue="Month"
          :caloriesBurned="month.caloriesBurned" :pointsEarned="month.pointsEarned" :duration="month.duration"
          />
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage.split(',')[0] === 'MyWorkoutStatsWeek' }">
        <div v-for="(month, index) in userAuthStore.filteredWorkoutData" :key="index" class="component-wrapper">
          <MyWorkoutStats v-for="(week, weekIndex) in month.weeks" :key="weekIndex" :data="week.data" :title="`${month.month}, ${week.week}`"
          :keyValue="`${month.month}${week.week}`" typeValue="Week"
          :caloriesBurned="week.caloriesBurned" :pointsEarned="week.pointsEarned" :duration="week.duration"
          />
        </div>
      </div>

      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage.split(',')[0] === 'MyWorkoutStatsDay' }">
        <div class="component-wrapper" v-for="(month, index) in userAuthStore.filteredWorkoutData" :key="index">
          <div v-for="(week, weekIndex) in month.weeks" :key="weekIndex" class="component-wrapper">
            <MyWorkoutStats v-for="(day, dayIndex) in week.days" 
            :key="dayIndex" :data="day.data" :title="`${day.day}`"
            :keyValue="`${month.month}${week.week}${day.day}`"  typeValue="Day"
            :caloriesBurned="day.caloriesBurned" :pointsEarned="day.pointsEarned" :duration="day.duration"
            />
          </div>
        </div>
      </div>

    </div>
  </main>
  <TheFooter v-if="userAuthStore.workoutTypes"/>
</template>

<style scoped>
.overlay-card {
  max-width: 600px !important;
}

</style>
