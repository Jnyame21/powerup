<script setup lang="ts">
import { onBeforeMount, ref } from 'vue';

const loading = ref(true)
const errorMessage = ref('Failed to load data')
interface Props {
  func?: any
}
const props = defineProps<Props>()
const func = props.func || null
const startLoading = ()=>{
  loading.value = true
  setTimeout(()=>{
    loading.value = false
  }, 60*1000)
}

onBeforeMount(()=>{
  startLoading()
})

const reloadData = async()=>{
  startLoading()
  try{
    await func()
    loading.value = false
  }
  catch(e){
    loading.value = false
    errorMessage.value = 'An error occurred while fetching data'
    return Promise.reject(e)
  }
}



</script>


<template>
<div class="loaderOverlay flex-all-c">
  <v-progress-circular :size="60" :width="8" v-if="loading" indeterminate></v-progress-circular>
  <p v-if="!loading" style="color: red">{{ errorMessage }}</p>
  <v-btn v-if="!loading && func" @click="reloadData" size="small" icon="mdi-reload" color="black"/>
</div>
</template>

<style scoped>

.loaderOverlay{
  width: 100% !important;
  height: 100% !important;
  background-color: white !important;
}


</style>
