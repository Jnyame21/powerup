import { defineStore } from 'pinia'
import { defaultAxiosInstance } from '@/utils/axiosInstance'
import axiosInstance from '@/utils/axiosInstance'
import { useElementsStore } from '@/stores/elementsStore'
import router from '@/router'
import type { UserData, WorkoutType, Workout, MonthData } from '@/utils/types_utils'
import { getCalendarData } from '@/utils/util'

export interface states {
  userData: UserData | null
  accessToken: string;
  isAuthenticated: boolean
  fetchedDataLoaded: boolean;
  currentDate: string;
  currentYearStartDate: string;
  currentYearEndDate: string;
  workoutTypes: WorkoutType[] | null;
  workoutData: Workout[];
  filteredWorkoutData: MonthData[]
}


export const useUserAuthStore = defineStore('userAuthStore', {
  state: (): states => {
    return {
      accessToken: '',
      userData: null,
      isAuthenticated: false,
      fetchedDataLoaded: false,
      currentDate: '',
      currentYearStartDate: '',
      currentYearEndDate: '',
      workoutTypes: null,
      workoutData: [],
      filteredWorkoutData: [],
    }
  },

  actions: {

    async logoutUser() {
      const elementsStore = useElementsStore()
      try {
        elementsStore.ShowLoadingOverlay()
        await axiosInstance.post('logout')
        this.accessToken = ''
        this.isAuthenticated = false
        this.userData = null
        elementsStore.HideLoadingOverlay()
        return;
      }
      catch (e) {
        elementsStore.HideLoadingOverlay()
        elementsStore.ShowOverlay('An error occurred while logging out', 'error')
        return Promise.reject(e)
      }
    },

    async getAppData() {
      try {
        const response = await axiosInstance.get('app/data')
        this.workoutTypes = response.data['workout_types']
        this.currentYearStartDate = response.data['current_year_start_date']
        this.currentYearEndDate = response.data['current_year_end_date']
      }
      catch (e) {
        return Promise.reject(e)
      }
    },

    async getWorkoutData() {
      try {
        const response = await axiosInstance.get('workout/data')
        this.workoutData = response.data['workouts']
        this.fetchedDataLoaded = true
      }
      catch (e) {
        return Promise.reject(e)
      }
    },

    async getUserData() {
      try {
        const response = await axiosInstance.get('user/data')
        this.userData = response.data
      }
      catch (error) {
        return Promise.reject(error)
      }
    },

    async userLogin(username: string, password: string) {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      try {
        const response = await defaultAxiosInstance.post('login', formData)
        this.accessToken = response.data['access']
        await this.getUserData()
        this.isAuthenticated = true
      }
      catch (error) {
        return Promise.reject(error)
      }
    },

    async UpdateToken() {
      try {
        const response = await defaultAxiosInstance.post('api/token/refresh/')
        this.accessToken = response.data.access
      }
      catch (error: any) {
        return Promise.reject(error)
      }
    },

    async getCurrentServerTime() {
      try {
        const response = await defaultAxiosInstance.get('server_time')
        return response.data
      }
      catch (error: any) {
        return Promise.reject(error)
      }
    },
  },
})

