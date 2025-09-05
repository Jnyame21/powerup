<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore'
import { useElementsStore } from '@/stores/elementsStore'
import Drawer from '@/components/Drawer.vue'


const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

const showOverlay = (element:string) => {
  const overlay = document.getElementById(element)
  if (overlay) {
    overlay.style.display = 'flex'
  }
}


</script>

<template>
  <Drawer v-if="userAuthStore.userData" />

  <header class="header">
    <div class="profile-container" v-if="userAuthStore.userData">
      <img v-if="userAuthStore.userData" @click.stop="elementsStore.drawer = !elementsStore.drawer" class="user-img" :src="typeof userAuthStore.userData.img ==='string' ? userAuthStore.userData.img : userAuthStore.userData.img?.url">
    </div>
    <div class="flex-all">
      <v-chip v-if="elementsStore.pusherState ==='connected'" color="green" :size="elementsStore.btnSize1">{{ elementsStore.pusherState }}</v-chip>
      <v-chip v-if="elementsStore.pusherState ==='connecting'" color="yellow" :size="elementsStore.btnSize1">{{ elementsStore.pusherState }}</v-chip>
    </div>
    <div>
      <v-icon v-if="!elementsStore.onDesk" @click.stop="elementsStore.navDrawer = !elementsStore.navDrawer" class="menu-icon" icon="mdi-menu" size="x-large" color="yellow" />
      <v-btn v-if="elementsStore.onDesk && userAuthStore.userData" @click="showOverlay('LogoutOverlay')" class="logout-btn" prepend-icon="mdi-logout">LOGOUT</v-btn>
    </div>
  </header>
</template>

<style scoped>
.header {
  height: 10vh;
  height: 10dvh;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0 !important;
  background-color: #333333;
  width: 100%
}

.year-info {
  font-size: .5rem;
  margin: .2em;
  color: yellow;
  font-family: monospace;
}

.profile-container {
  width: max-content;
  display: flex;
  align-items: center;
  background-color: white;
  border-radius: 10%;
  padding: .2em;
  margin-left: .3em;
}

.user-img {
  width: 40px !important;
  min-width: 40px !important;
  height: 40px !important;
  border-radius: 40% !important;
  object-fit: cover !important;
}

.user-img:hover {
  box-shadow: 0px 0px 10px black;
  cursor: pointer;
}

.notice {
  box-shadow: 0px 0px 2px black;
  border-radius: .1em;
  cursor: pointer;
  padding: .1em .2em;
  margin-right: .2em;
  width: 40px;
}

.menu-icon {
  margin-right: .2em;
}

.logout-btn {
  background-color: #ff4d4d;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: .3em;
  cursor: pointer;
  margin-right: .7em;
}

.logout-btn:hover {
  background-color: #e60000;
}


@media screen and (min-width: 370px) {
  .year-info {
    font-size: .55rem;
  }

}

@media screen and (min-width: 460px) {
  .profile-container {
    margin-left: .5em;
  }

  .menu-icon {
    margin-right: .5em;
  }

  .year-info {
    font-size: .6rem;
  }

}

@media screen and (min-width: 576px) {
  .profile-container {
    margin-left: 0.6em;
  }

  .user-img {
    width: 45px;
    height: 35px;
  }

  .year-info {
    font-size: .8rem;
  }
}

@media screen and (min-width: 1000px) {
  .year-info {
    font-size: 1rem;
  }
}
</style>
