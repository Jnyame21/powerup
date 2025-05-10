<script setup lang="ts">
import { computed, ref } from 'vue';
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';
import { formatDate } from '@/utils/util';
import type { Challenge, ChallengeParticipant, UserProfile, UserProfileTwo } from '@/utils/types_utils'
import axiosInstance from '@/utils/axiosInstance';
import { AxiosError } from 'axios';
import NoData from '@/components/NoData.vue';
import pusher from '@/utils/pusher';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()
const selectedAdminId = ref<number | null>(null)
const selectedMemberId = ref<number | null>(null)
const memberToAddUsername = ref('')
const challengeItem = ref<Challenge | null>(null)

interface Props {
  id: number;
}

const props = defineProps<Props>()
const communityId = props.id
const communityData = computed(()=>{
  return userAuthStore.communitiesData.find(item=> item.id === props.id)
})

const challengeData = ref<Challenge>({
  id: 0,
  name: '',
  description: '',
  workout_types: [],
  start_date: '',
  end_date: '',
  date: '',
  participants: []
})

const channel = pusher.subscribe(`community_${communityId}`)
channel.bind('community_members_update', (sentData: {data: UserProfile[], action: string})=>{
  const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
  if (communityObj){
    if (sentData.action === 'add'){
      sentData.data.forEach(item=>{
        const memberObj = communityObj.members.find(subItem=> subItem.id === item.id)
        memberObj ? null : communityObj.members.unshift(item)
      })
    }
    else if (sentData.action === 'remove'){
      sentData.data.forEach(item=>{
        if (userAuthStore.userData?.username === item.username){
          const communityName = communityData.value?.name || ''
          const communityIndex = userAuthStore.communitiesData.findIndex(item=> item.id === communityId)
          communityIndex !== -1 ? userAuthStore.communitiesData.splice(communityIndex, 1) : null
          elementsStore.activePage === `MyCommunity,${communityId}` ? elementsStore.activePage = 'MyWorkouts' : null
          elementsStore.ShowOverlay(`You have been removed from the community "${communityName}"`, 'green')
        }
        else {
          const itemIndex = communityObj.members.findIndex(subItem=> subItem.id === item.id)
          itemIndex !== -1 ? communityObj.members.splice(itemIndex, 1) : null
        }
      })
    }
  }
})
channel.bind('community_admins_update', (sentData: {data: UserProfileTwo[], action: string})=>{
  const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
  if (communityObj){
    if (sentData.action === 'add'){
      sentData.data.forEach(item=>{
        const adminObj = communityObj.admins.find(subItem=> subItem.id === item.id)
        adminObj ? null : communityObj.admins.push(item)
      })
    }
    else if (sentData.action === 'remove'){
      sentData.data.forEach(item=>{
        const itemIndex = communityObj.admins.findIndex(subItem=> subItem.id === item.id)
        itemIndex !== -1 ? communityObj.admins.splice(itemIndex, 1) : null
      })
    }
  }
})
channel.bind('community_deleted', (username: string)=>{
  const communityName = communityData.value?.name || ''
  const communityIndex = userAuthStore.communitiesData.findIndex(item=> item.id === communityId)
  communityIndex !== -1 ? userAuthStore.communitiesData.splice(communityIndex, 1) : null
  elementsStore.activePage === `MyCommunity,${communityId}` ? elementsStore.activePage = 'MyWorkouts' : null
  userAuthStore.userData?.username === username ? null : elementsStore.ShowOverlay(`${username} has deleted the community "${communityName}"`, 'green')
})
channel.bind('challenge_participants_update', (sentData: {data: ChallengeParticipant; action: string; challenge_id: number})=>{
  const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
  if (communityObj){
    const challengeObj = communityObj.challenges.find(item=> item.id === sentData.challenge_id)
    if (challengeObj){
      if (sentData.action === 'add'){
        const participantObj = challengeObj.participants.find(item=> item.id === sentData.data.id)
        participantObj ? Object.assign(participantObj, sentData.data) : challengeObj.participants.unshift(sentData.data)
      }
      else if (sentData.action === 'remove'){
        const ItemIndex = challengeObj.participants.findIndex(subItem=> subItem.id === sentData.data.id)
        ItemIndex !== -1 ? challengeObj.participants.splice(ItemIndex,  1) : null
      }
    }
  }
})
channel.bind('challenge_added', (sentData: {challenge: Challenge; username: string})=>{
  const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
  if (communityObj){
    const existingChallenge = communityObj.challenges.find(item=> item.id === sentData.challenge.id)
    existingChallenge ? null : communityObj.challenges.unshift(sentData.challenge)
  }
  userAuthStore.userData?.username === sentData.username ? null : elementsStore.ShowOverlay(`${sentData.username} has added the challenge "${sentData.challenge.name}"`, 'green')
})
channel.bind('challenge_deleted', (sentData: {challenge_id: number; challenge_name: string; username: string})=>{
  const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
  if (communityObj){
    const challengeIndex = communityObj.challenges.findIndex(item=> item.id === sentData.challenge_id)
    challengeIndex !== -1 ? communityObj.challenges.splice(challengeIndex, 1) : null
  }
  userAuthStore.userData?.username === sentData.username ? null : elementsStore.ShowOverlay(`${sentData.username} has deleted the challenge "${sentData.challenge_name}"`, 'green')
})


const exitCommunity = async () => {
  if (communityData.value && communityData.value.admins.find(item=> item.username === userAuthStore.userData?.username) && communityData.value.admins.length === 1){
    elementsStore.ShowOverlay("You are the only admin in this community. Please add another admin before exiting.", 'red')
    return;
  }
  const formData = new FormData()
  formData.append('type', 'exitCommunity')
  formData.append('communityId', communityId.toString() || '')
  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('workout/data', formData)
    const communityName = communityData.value?.name || ''
    const communityIndex = userAuthStore.communitiesData.findIndex(item=> item.id === communityId)
    communityIndex !== -1 ? userAuthStore.communitiesData.splice(communityIndex, 1) : null
    elementsStore.activePage = 'MyWorkouts'
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay(`You have successfully exited from the community "${communityName}"`, 'green')
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

const addCommunityAdmin = async () => {
  const formData = new FormData()
  formData.append('type', 'addCommunityAdmin')
  formData.append('communityId', communityId.toString() || '')
  formData.append('memberId', selectedMemberId.value?.toString() || '')
  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('workout/data', formData)
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const existingAdmin = communityObj.admins.find(item=> item.id === selectedMemberId.value as number)
      if (!existingAdmin){
        const existingMember = communityObj.members.find(item=> item.id === selectedMemberId.value as number)
        existingMember ? communityObj.admins.unshift({id: existingMember.id, username: existingMember.username}) : null
      }
    }
    selectedMemberId.value = null
    HideShowOverlay(`AddAdminOverlay${props.id}`, `CommunityAdminsOverlay${props.id}`)
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

const removeCommunityAdmin = async (admin_id: number) => {
  const formData = new FormData()
  formData.append('type', 'removeCommunityAdmin')
  formData.append('communityId', communityId.toString())
  formData.append('adminId', admin_id.toString())
  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('workout/data', formData)
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const itemIndex = communityObj.admins.findIndex(item=> item.id === admin_id)
      itemIndex !== -1 ? communityObj.admins.splice(itemIndex, 1) : null
    }
    closeOverlay(`CommunityAdminsOverlay${props.id}`)
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

const addCommunityMember = async () => {
  const formData = new FormData()
  formData.append('type', 'addCommunityMember')
  formData.append('communityId', communityId.toString())
  formData.append('username', memberToAddUsername.value)
  elementsStore.ShowLoadingOverlay()
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const responseData:UserProfile = response.data
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const existingMember = communityObj.members.find(item=> item.id === responseData.id)
      existingMember ? null : communityObj.members.unshift(responseData)
    }
    memberToAddUsername.value = ''
    HideShowOverlay(`AddMemberOverlay${props.id}`, `CommunityMembersOverlay${props.id}`)
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

const removeCommunityMember = async (member_id: number) => {
  const formData = new FormData()
  formData.append('type', 'removeCommunityMember')
  formData.append('communityId', communityId.toString())
  formData.append('memberId', member_id.toString())
  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('workout/data', formData)
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const itemIndex = communityObj.members.findIndex(item=> item.id === member_id)
      itemIndex !== -1 ? communityObj.members.splice(itemIndex, 1) : null
    }
    closeOverlay(`CommunityMembersOverlay${props.id}`)
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

const createChallenge = async () => {
  if (challengeData.value.workout_types.length === 0){
    elementsStore.ShowOverlay('Please select at least one workout type', 'red')
    return;
  }
  if (new Date(challengeData.value.start_date) > new Date(challengeData.value.end_date)){
    elementsStore.ShowOverlay('The start date cannot be after the end date', 'red')
    return;
  }
  const formData = new FormData()
  formData.append('type', 'createChallenge')
  formData.append('dataObj', JSON.stringify(challengeData.value))
  formData.append('communityId', communityId.toString() || '')
  elementsStore.ShowLoadingOverlay()
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const responseData: Challenge = response.data
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const existingChallenge = communityObj.challenges.find(item=> item.id === responseData.id)
      existingChallenge ? null : communityObj.challenges.unshift(responseData)
    }
    challengeData.value.name = ''
    challengeData.value.description = ''
    challengeData.value.workout_types = []
    challengeData.value.start_date = ''
    challengeData.value.end_date = ''
    elementsStore.HideLoadingOverlay()
    elementsStore.ShowOverlay(`You have added the challenge "${responseData.name}"`, 'green')
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

const joinChallenge = async (challenge: Challenge) => {
  const formData = new FormData()
  formData.append('type', 'joinChallenge')
  formData.append('challengeId', challenge.id.toString())
  elementsStore.ShowLoadingOverlay()
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const responseData: ChallengeParticipant = response.data
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const challengeObj = communityObj.challenges.find(item=> item.id === challenge.id)
      if (challengeObj){
        const existingParticipant = challengeObj.participants.find(item=> item.id === responseData.id)
        existingParticipant ? null : challengeObj.participants.unshift(responseData)
      }
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

const exitChallenge = async (challenge: Challenge) => {
  const formData = new FormData()
  formData.append('type', 'exitChallenge')
  formData.append('challengeId', challenge.id.toString())
  elementsStore.ShowLoadingOverlay()
  try {
    const response = await axiosInstance.post('workout/data', formData)
    const responseData: ChallengeParticipant = response.data
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const challengeObj = communityObj.challenges.find(item=> item.id === challenge.id)
      if (challengeObj){
        const participantIndex = challengeObj.participants.findIndex(item=> item.id === responseData.id)
        participantIndex !== -1 ? challengeObj.participants.splice(participantIndex, 1) : null
      }
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

const deleteChallenge = async (challenge: Challenge) => {
  const formData = new FormData()
  formData.append('type', 'deleteChallenge')
  formData.append('itemId', challenge.id.toString())
  elementsStore.ShowLoadingOverlay()
  try {
    await axiosInstance.post('workout/data', formData)
    const communityObj = userAuthStore.communitiesData.find(item=> item.id === communityId)
    if (communityObj){
      const challengeIndex = communityObj.challenges.findIndex(item=> item.id === challenge.id)
      challengeIndex !== -1 ? communityObj.challenges.splice(challengeIndex, 1) : null
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

const HideShowOverlay = (overlay_to_hide: string, overlay_to_show: string) => {
  closeOverlay(overlay_to_hide)
  showOverlay(overlay_to_show)
}

const showOverlay = (element: string, challenge_item: Challenge | null=null) => {
  challengeItem.value = challenge_item
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
  <div :id="`MyCommunity,${props.id}`" class="content-wrapper" v-show="elementsStore.activePage === `MyCommunity,${props.id}`" :class="{ 'is-active-page': elementsStore.activePage === `MyCommunity,${props.id}` }">
    
    <!-- community code overlay -->
    <div :id="`CommunityCodeOverlay${props.id}`" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay(`CommunityCodeOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
        <div class="overlay-card-info-container">
          <v-chip :size="elementsStore.btnSize1" color="blue">CODE</v-chip>
        </div>
        <div class="overlay-card-content-container">
          <v-chip v-if="communityData" :size="elementsStore.btnSize1" color="green">{{ communityData.join_code }}</v-chip>
          <v-icon class="ml-2" @click="elementsStore.copyToClipboard(communityData?.join_code || '')" size="x-small" icon="mdi-content-copy"/>
        </div>
        <div class="overlay-card-action-btn-container"></div>
      </div>
    </div>

    <!-- community description overlay -->
    <div :id="`CommunityDescriptionOverlay${props.id}`" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay(`CommunityDescriptionOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
        <div class="overlay-card-info-container">
          <v-chip :size="elementsStore.btnSize1" color="blue">DESCRIPTION</v-chip>
        </div>
        <div class="overlay-card-content-container">
          {{ communityData?.description }}
        </div>
        <div class="overlay-card-action-btn-container"></div>
      </div>
    </div>

    <!-- community admins overlay -->
    <div :id="`CommunityAdminsOverlay${props.id}`" class="overlay">
      <div class="overlay-card">
        <v-btn @click="closeOverlay(`CommunityAdminsOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
        <div class="overlay-card-info-container">
          <v-chip v-if="communityData" :size="elementsStore.btnSize1" color="blue">ADMIN [{{ communityData.admins.length }}]</v-chip>
          <v-btn class="ml-5" v-if="communityData?.admins.find(item=> item.username === userAuthStore.userData?.username)" @click="showOverlay(`AddAdminOverlay${props.id}`)" color="blue" icon="mdi-plus" size="x-small"/>
        </div>
        <div v-if="communityData" class="overlay-card-content-container">
          <v-chip class="ma-2" v-for="_item_ in communityData.admins" :key="_item_.id" :size="elementsStore.btnSize1" color="green">
            {{ _item_.username }}
            <v-icon v-if="communityData?.admins.find(item=> item.username === userAuthStore.userData?.username) && userAuthStore.userData?.username !==_item_.username" class="ml-2" @click="elementsStore.ShowDeletionOverlay(()=> removeCommunityAdmin(_item_.id), `Are you sure you want to remove ${_item_.username} from the community admin`)" size="x-small" icon="mdi-delete"/>
          </v-chip>
        </div>
        <div class="overlay-card-action-btn-container"></div>
      </div>
    </div>

    <!-- Community Members Overlay -->
    <div :id="`CommunityMembersOverlay${props.id}`" class="overlay">
      <div class="overlay-card view-card-1">
        <v-btn @click="closeOverlay(`CommunityMembersOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
        <div class="overlay-card-info-container" v-if="communityData">
          <v-chip :size="elementsStore.btnSize1" color="blue">{{ communityData.members.length }} MEMBERS</v-chip>
          <v-btn class="ml-5" v-if="communityData?.admins.find(item=> item.username === userAuthStore.userData?.username)" @click="showOverlay(`AddMemberOverlay${props.id}`)" color="blue" icon="mdi-plus" size="x-small"/>
        </div>
        <div class="overlay-card-content-container">
          <v-table fixed-header class="table" v-if="communityData">
            <thead>
              <tr>
                <th class="table-head"></th>
                <th class="table-head">USERNAME</th>
                <th class="table-head">GENDER</th>
                <th class="table-head">AGE</th>
                <th class="table-head">COUNTRY</th>
                <th class="table-head">CITY</th>
                <th class="table-head">HEIGHT (CM)</th>
                <th class="table-head">WEIGHT (KG)</th>
                <th class="table-head">ACTION</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="_item_ in communityData.members" :key="_item_.id">
                <td class="table-data">
                  <v-avatar size="40" class="ma-2">
                    <v-img :src="_item_.img" />
                  </v-avatar>
                </td>
                <td class="table-data">
                  <v-chip size="x-small">{{ _item_.username }}</v-chip>
                </td>
                <td class="table-data">
                  <v-chip size="x-small">{{ _item_.gender }}</v-chip>
                </td>
                <td class="table-data">
                  <v-chip size="x-small">{{ _item_.age }}</v-chip>
                </td>
                <td class="table-data">
                  <v-chip size="x-small">{{ _item_.country }}</v-chip>
                </td>
                <td class="table-data">
                  <v-chip size="x-small">{{ _item_.city }}</v-chip>
                </td>
                <td class="table-data">
                  <v-chip v-if="_item_.height" size="x-small">{{ _item_.height }}</v-chip>
                </td>
                <td class="table-data">
                  <v-chip v-if="_item_.weight" size="x-small">{{ _item_.weight }}</v-chip>
                </td>
                <td class="table-data">
                  <v-btn class="ml-5" v-if="communityData.admins.find(item=> item.username === userAuthStore.userData?.username)" @click="elementsStore.ShowDeletionOverlay(()=> removeCommunityMember(_item_.id), `Are you sure you want to remove ${_item_.username} from the community`)" color="red" icon="mdi-delete" size="x-small"/>
                </td>
              </tr>
            </tbody>
          </v-table>
        </div>
        <div class="overlay-card-action-btn-container"></div>
      </div>
    </div>

    <!-- Challenge Leaderboard Overlay -->
    <div :id="`ChallengeLeaderboardOverlay${props.id}`" class="overlay">
      <div class="overlay-card" v-if="challengeItem">
        <v-btn @click="closeOverlay(`ChallengeLeaderboardOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
        <div class="overlay-card-info-container">
          <v-chip :size="elementsStore.btnSize1" color="blue">{{ challengeItem.name }}</v-chip>
        </div>
        <div class="overlay-card-content-container">
            <v-card-title class="text-h6 font-weight-bold">
              <v-icon class="me-2" color="amber">mdi-trophy</v-icon>Leaderboard
            </v-card-title>
            <v-divider class="my-2" />
            <v-list>
              <v-list-item v-for="(participant, index) in challengeItem.participants.sort((a, b)=> b.points - a.points)" :key="participant.id">
                <template #prepend>
                  <v-avatar color="indigo" size="32">
                    <span class="white--text text-caption font-weight-bold">{{ index + 1 }}</span>
                  </v-avatar>
                </template>
                <template #default>
                  <v-chip color="blue" variant="flat" size="small">{{ participant.username }}</v-chip>
                </template>
                <template #append>
                  <v-chip color="green" variant="flat" size="small" class="font-weight-bold">{{ participant.points }} XP</v-chip>
                </template>
              </v-list-item>
            </v-list>
        </div>
        <div class="overlay-card-action-btn-container"></div>
      </div>
    </div>

    <!-- Add Member Overlay -->
    <div :id="`AddMemberOverlay${props.id}`" class="overlay">
        <div class="overlay-card">
          <v-btn @click="closeOverlay(`AddMemberOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
          <div class="overlay-card-content-container" v-if="communityData" style="margin-top: 3em;">
            <v-text-field class="input-field" v-model="memberToAddUsername" label="USERNAME" hint="Enter the username of the person you want to add" density="comfortable" type="text" clearable persistent-hint />
          </div>
          <div class="overlay-card-action-btn-container">
            <v-btn @click="addCommunityMember()" :disabled="!(memberToAddUsername)" :ripple="false" variant="flat" type="submit" color="black" size="small" append-icon="mdi-checkbox-marked-circle">ADD</v-btn>
          </div>
        </div>
      </div>

    <!-- Add Admin Overlay -->
    <div :id="`AddAdminOverlay${props.id}`" class="overlay">
        <div class="overlay-card">
          <v-btn @click="closeOverlay(`AddAdminOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
          <div class="overlay-card-content-container" v-if="communityData" style="margin-top: 3em;">
            <v-select class="input-field" v-model="selectedMemberId" label="MEMBER" :items="communityData.members.filter(item=> !communityData?.admins.map(subItem=> subItem.id).includes(item.id)) || []" item-title="username" item-value="id" hint="Select the member you want give admin permissions to" density="comfortable" clearable persistent-hint />
          </div>
          <div class="overlay-card-action-btn-container">
            <v-btn @click="addCommunityAdmin()" :disabled="!(selectedMemberId)" :ripple="false" variant="flat" type="submit" color="black" size="small" append-icon="mdi-checkbox-marked-circle">ADD</v-btn>
          </div>
        </div>
      </div>

    <!-- Create Challenge Overlay -->
    <div :id="`CreateChallengeOverlay${props.id}`" class="overlay">
        <div class="overlay-card">
          <v-btn @click="closeOverlay(`CreateChallengeOverlay${props.id}`)" color="red" size="small" variant="flat" class="close-btn">X</v-btn>
          <div class="overlay-card-info-container">
            <v-chip :size="elementsStore.btnSize2" color="red">NB: Fields with [*] are mandatory.</v-chip>
          </div>
          <div class="overlay-card-content-container">
            <v-text-field class="input-field" v-model="challengeData.name" label="NAME [*]" hint="Enter a name for the challenge" density="comfortable" type="text" clearable persistent-hint />
            <v-text-field class="input-field" v-model="challengeData.start_date" label="START DATE [*]" hint="Select the start date of the challenge" density="comfortable" type="date" clearable persistent-hint />
            <v-text-field class="input-field" v-model="challengeData.end_date" label="END DATE [*]" hint="Select the end date of the challenge" density="comfortable" type="date" clearable persistent-hint />
            <v-select class="input-field" v-model="challengeData.workout_types" label="WORKOUT TYPES [*]" :items="userAuthStore.workoutTypes || []" item-title="name" multiple item-value="id" hint="Select all the workout types that apply to the challenge" density="comfortable" clearable persistent-hint />
            <v-textarea class="input-field" v-model="challengeData.description" label="DESCRIPTION [*]" hint="Give a brief description about the challenge" density="comfortable" rows="5" no-resize clearable persistent-hint prepend-inner-icon="mdi-text" />
          </div>
          <div class="overlay-card-action-btn-container">
            <v-btn @click="createChallenge()" :disabled="!(challengeData.name && challengeData.description && challengeData.start_date && challengeData.end_date)" :ripple="false" variant="flat" type="submit" color="black" size="small" append-icon="mdi-checkbox-marked-circle">CREATE</v-btn>
          </div>
        </div>
      </div>

    <div class="content-header" v-if="communityData">
      <h4 class="content-header-title">{{ communityData.name.toUpperCase() }}</h4>
    </div>
    <div class="content-header btn-container" v-if="communityData">
      <v-btn @click="showOverlay(`CommunityDescriptionOverlay${props.id}`)" color="blue" icon="mdi-clipboard-text" :size="elementsStore.btnSize1"/>
      <v-btn class="ml-5" @click="showOverlay(`CommunityCodeOverlay${props.id}`)" color="blue" icon="mdi-account-plus" :size="elementsStore.btnSize1"/>
      <v-btn class="ml-5" @click="showOverlay(`CommunityAdminsOverlay${props.id}`)" color="blue" icon="mdi-account-multiple" :size="elementsStore.btnSize1"/>
      <v-btn class="ml-5" @click="showOverlay(`CommunityMembersOverlay${props.id}`)" color="blue" icon="mdi-account-group" :size="elementsStore.btnSize1"/>
      <v-btn class="ml-5" v-if="communityData.admins.find(item=> item.username === userAuthStore.userData?.username)" @click="showOverlay(`CreateChallengeOverlay${props.id}`)" color="blue" prepend-icon="mdi-plus" :size="elementsStore.btnSize1">CHALLENGE</v-btn>
      <v-btn class="ml-5" @click="elementsStore.ShowDeletionOverlay(()=> exitCommunity(), 'Are you sure you want to exit from this community?')" color="red" :size="elementsStore.btnSize1">EXIT</v-btn>
    </div>
    <NoData message="There are no challenges yet." v-if="communityData && communityData.challenges.length === 0" />
    <div class="items-container" v-if="communityData && communityData.challenges.length > 0">
      <v-container fluid>
      <v-row dense>
        <v-col v-for="challenge in communityData.challenges" :key="challenge.id" cols="12" sm="12" md="12" lg="6">
          <v-card class="pa-4" elevation="0" rounded="lg">
            <v-card-title class="text-h6 font-weight-bold text-wrap" style="word-wrap: break-word;">{{ challenge.name }}</v-card-title>
            <v-card-subtitle class="text-caption text-uppercase text-primary text-wrap" style="word-wrap: break-word;">
              <v-chip class="ma-1" v-for="(item, index) in challenge.workout_types" :key="index" size="small" color="blue">{{ item }}</v-chip>
            </v-card-subtitle>
            <v-card-text class="my-2">
              <div class="mb-5">
                <div><pre>{{ challenge.description }}</pre></div>
              </div>
              <div class="d-flex justify-space-between my-2">
                <div>
                  <strong>From</strong> <v-chip size="x-small" color="blue">{{ formatDate(challenge.start_date, 'short') }}</v-chip>
                  <strong>  To  </strong>
                  <v-chip size="x-small" color="blue">{{ formatDate(challenge.end_date, 'short') }}</v-chip>
                </div>
              </div>
            </v-card-text>
            <v-card-actions class="justify-space-around">
              <v-btn v-if="userAuthStore.userData && !challenge.participants.map(item=> item.username).includes(userAuthStore.userData.username)" color="blue" :size="elementsStore.btnSize2" @click="elementsStore.ShowDeletionOverlay(()=> joinChallenge(challenge), 'Are you sure you want to join this challenge?')">JOIN</v-btn>
              <v-btn v-if="userAuthStore.userData && challenge.participants.map(item=> item.username).includes(userAuthStore.userData.username)" color="blue" :size="elementsStore.btnSize2" @click="elementsStore.ShowDeletionOverlay(()=> exitChallenge(challenge), 'Are you sure you want to exit from this challenge?')">EXIT</v-btn>
              <v-btn color="blue" :size="elementsStore.btnSize2" @click="showOverlay(`ChallengeLeaderboardOverlay${props.id}`, challenge)" append-icon="mdi-trophy">Leaderboard</v-btn>
              <v-btn v-if="communityData.admins.find(item=> item.username === userAuthStore.userData?.username)" icon="mdi-delete" :size="elementsStore.btnSize2" color="red" @click="elementsStore.ShowDeletionOverlay(()=> deleteChallenge(challenge), 'Are you sure you want to delete this challenge?')"/>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    </div>
  </div>
</template>

<style scoped>

.btn-container{
  min-height: 15% !important;
}
.overlay-card{
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
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
  font-family: Verdana, Geneva, Tahoma, sans-serif;
}

</style>
