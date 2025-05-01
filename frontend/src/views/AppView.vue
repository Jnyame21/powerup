<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore'
import { useElementsStore } from '@/stores/elementsStore'
import { useHead } from '@vueuse/head';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';
import { onMounted, computed, watch } from 'vue';
import NavContainerDesk from '@/components/NavContainerDesk.vue';
import NavContainerMob from '@/components/NavContainerMob.vue';
import MyWorkouts from '@/components/MyWorkouts.vue';
import { getCalendarData, getWeekNumberInMonth } from '@/utils/util';
import MyWorkoutStats from '@/components/MyWorkoutStats.vue';

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

onMounted(()=>{
  elementsStore.activePage = localStorage.getItem('activePage') || 'MyWorkouts'
})

const workouts = computed(()=>{
  return userAuthStore.workoutData
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



</script>

<template>
  <TheHeader v-if="userAuthStore.workoutTypes"/>
  <main class="main" v-if="userAuthStore.workoutTypes">
    <NavContainerMob v-if="!elementsStore.onDesk" />
    <NavContainerDesk v-if="elementsStore.onDesk" />
    <div class="pages-container">
      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'MyWorkouts' }">
        <MyWorkouts/>
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
