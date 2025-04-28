<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore'
import { useElementsStore } from '@/stores/elementsStore'
import { useHead } from '@vueuse/head';
import TheHeader from '@/components/TheHeader.vue';
import TheFooter from '@/components/TheFooter.vue';
import { onMounted } from 'vue';
import NavContainerDesk from '@/components/NavContainerDesk.vue';
import NavContainerMob from '@/components/NavContainerMob.vue';
import MyWorkouts from '@/components/MyWorkouts.vue';

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
  elementsStore.activePage = 'MyWorkouts'
})

</script>

<template>
  <TheHeader v-if="userAuthStore.fetchedDataLoaded"/>
  <main class="main" v-if="userAuthStore.fetchedDataLoaded">
    <NavContainerMob v-if="!elementsStore.onDesk" />
    <NavContainerDesk v-if="elementsStore.onDesk" />
    <div class="pages-container">
      <div class="component-wrapper" :class="{ 'is-active-component': elementsStore.activePage === 'MyWorkouts' }">
        <MyWorkouts/>
      </div>
    </div>
  </main>
  <TheFooter v-if="userAuthStore.fetchedDataLoaded"/>
</template>

<style scoped>
.overlay-card {
  max-width: 600px !important;
}

</style>
