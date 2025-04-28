<script setup lang="ts">

interface Props {
    message?: string;
}

const { message } = defineProps<Props>()


</script>


<template>
<div class="no-data">
    <p v-if="message">{{ message }}</p>
    <p v-if="!message">No Data Yet</p>
    <a></a>
</div>
</template>

<style scoped>



</style>