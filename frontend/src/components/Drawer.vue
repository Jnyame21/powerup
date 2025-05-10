
<script setup lang="ts">
import { useUserAuthStore } from '@/stores/userAuthStore';
import { useElementsStore } from '@/stores/elementsStore';

const userAuthStore = useUserAuthStore()
const elementsStore = useElementsStore()

const drawer = document.getElementById('Drawer')
document.addEventListener('click', (event: MouseEvent)=>{
  if (drawer?.style.display !== 'none'){
    if (!drawer?.contains(event?.target as Node)){
      elementsStore.drawer = false
    }
  }
})


</script>


<template>
    <div id="Drawer" class="drawer-container" v-show="elementsStore.drawer">
      <v-list class="drawer-list">
        <div class="flex-all-c profile-image-container">
          <img class="img" v-if="userAuthStore.userData" :src="typeof userAuthStore.userData?.img ==='string' ? userAuthStore.userData.img : userAuthStore.userData?.img?.url">
          <img class="img" v-if="!userAuthStore.userData" src="/default_img_2.webp">
        </div>

        <v-card-title v-if="userAuthStore.userData" class="drawer-head">PROFILE</v-card-title>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-card-account-details-outline">
          <v-list-item-title class="drawer-title">
            USERNAME
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.username }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item class="drawer-item" v-if="userAuthStore.userData && userAuthStore.userData.gender.toLowerCase() === 'male'" prepend-icon="mdi-gender-male">
          <v-list-item-title class="drawer-title">
            GENDER
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.gender }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-list-item class="drawer-item" v-if="userAuthStore.userData && userAuthStore.userData.gender.toLowerCase() === 'female'" prepend-icon="mdi-gender-female">
          <v-list-item-title class="drawer-title">
            GENDER
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.gender }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-list-item class="drawer-item" v-if="userAuthStore.userData && userAuthStore.userData.gender.toLowerCase() !== 'male' && userAuthStore.userData.gender !== 'female'" prepend-icon="mdi-gender-male-female">
          <v-list-item-title class="drawer-title">
            GENDER
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.gender }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-email-outline">
          <v-list-item-title class="drawer-title">
            EMAIL
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.email }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-flag">
          <v-list-item-title class="drawer-title">
            COUNTRY
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.country }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-city">
          <v-list-item-title class="drawer-title">
            CITY
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.city }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-ruler">
          <v-list-item-title class="drawer-title">
            HEIGHT
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.height }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-scale-bathroom">
          <v-list-item-title class="drawer-title">
            WEIGHT
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.weight }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-human-child">
          <v-list-item-title class="drawer-title">
            AGE
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            {{ userAuthStore.userData.age }}
          </v-list-item-subtitle>
        </v-list-item>

        <v-list-item v-if="userAuthStore.userData" class="drawer-item" prepend-icon="mdi-account-details">
          <v-list-item-title class="drawer-title">
            BIO
          </v-list-item-title>
          <v-list-item-subtitle class="drawer-subtitle">
            <a class="bio-link" @click="()=> elementsStore.ShowOverlay(userAuthStore.userData?.bio || '', 'black')">VIEW</a>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
    </div>
</template>


<style scoped>

.profile-image-container{
  width: 100%;
  padding: 10px;
  height: 190px;
}

.profile-image-container .img{
  border-radius: 30%;
  width: 150px;
  height: 150px;
}
.bio-link:hover{
  cursor: pointer;
  text-decoration: underline;
}

</style>
