<script setup lang="ts">

const year = new Date().getFullYear()

</script>

<template>
    <footer class="footer flex-all">
        <div class="footer-content flex-all">
            <p class="footer-text">© {{ year }} PowerUp. All rights reserved.</p>
        </div>
    </footer>
</template>

<style scoped>

.footer {
    background-color: #333333;
    padding: 5px;
    width: 100%;
    height: 5vh;
    height: 5dvh;
    text-align: center;
    bottom: 0;
    color: yellow;
}

.footer-text {
    font-size: 0.875rem;
    margin: 0; 
    font-weight: bold;
}



</style>