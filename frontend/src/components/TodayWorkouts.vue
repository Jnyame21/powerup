<script setup lang="ts">
import { computed, ref} from 'vue';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import { formatDate, formatDuration } from '@/utils/util';
import type { Workout } from '@/utils/types_utils';
import NoData from '@/components/NoData.vue';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

const todayWorkoutData = computed(()=>{
  const workoutData:{[workout_type: string]: Workout[]} = {}
  userAuthStore.workoutData.filter(item=> item.date === userAuthStore.currentDate).forEach(item=> {
    if (!workoutData[item.workout_type]){
      workoutData[item.workout_type] = []
    }
    workoutData[item.workout_type]?.push(item)
  })
  return workoutData
})

</script>

<template>
  <div id="TodayWorkouts" class="content-wrapper" v-show="elementsStore.activePage === 'TodayWorkouts'" :class="{ 'is-active-page': elementsStore.activePage === 'TodayWorkouts' }">
    
    <div class="content-header">
      <h4 class="content-header-title">{{ formatDate(userAuthStore.currentDate, 'long') }}</h4>
    </div>
    <div class="content-header">
    </div>
    <NoData message="Looks like you didn't work out during this time." v-if="Object.keys(todayWorkoutData).length === 0" />
    <div class="items-container" v-if="Object.keys(todayWorkoutData).length > 0">
      <v-container fluid>
      <v-row dense>
        <v-col v-for="[key, value] in Object.entries(todayWorkoutData)" :key="key" cols="12" sm="6" md="6" lg="4">
          <v-card class="workout-card" elevation="1" rounded="lg">
            <v-card-title class="text-h6 font-weight-bold">{{ key.toUpperCase() }}</v-card-title>
            <v-img :src="userAuthStore.workoutTypes?.find(item=> item.name === key)?.thumbnail" height="200" cover ></v-img>
            <v-card-title class="card-title">
              DURATION <v-icon icon="mdi-timer" color="green" size="small"/>: <v-chip color="blue" size="small">{{ formatDuration(value.map(item=> item.duration).reduce((total, num)=> total + Number(num), 0)) }}</v-chip>
            </v-card-title>
            <v-card-title class="card-title">
              POINTS EARNED <v-icon icon="mdi-star" color="yellow" size="small"/>: <v-chip color="blue" size="small">{{ Number(value.map(item=> item.points).reduce((total, num)=> total + Number(num), 0)) }} XP</v-chip>
            </v-card-title>
            <v-card-title class="card-title">
              CALORIES BURNED <v-icon icon="mdi-fire" color="red" size="small"/>: <v-chip color="blue" size="small">{{ Number(value.map(item=> item.calories_burned).reduce((total, num)=> total + Number(num), 0)) }} kcal</v-chip>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    </div>
  </div>
</template>

<style scoped>

.items-container{
  width: 100% !important;
  height: 80% !important;
  overflow-y: auto !important;
  display: flex !important;
  flex-wrap: wrap !important;
  justify-content: space-around !important;
  align-items: flex-start !important;
}
.workout-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: max-content !important;
  margin: .1em !important;
}
.card-title{
  width: 100% !important;
  min-width: max-content !important;
  font-size: .75rem;
  font-weight: bold;
  font-family: Verdana, Geneva, Tahoma, sans-serif;
}

</style>
