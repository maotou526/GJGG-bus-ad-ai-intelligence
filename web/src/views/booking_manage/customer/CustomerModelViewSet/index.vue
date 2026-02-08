<!--
 * @Description: 客户管理
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
-->
<template>
    <BookingCustomersPage />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import BookingCustomersPage from './BookingCustomersPage.vue';

export default defineComponent({
    name: "CustomerModelViewSet",
    components: {
        BookingCustomersPage
    }
});
</script>

<style scoped> 
</style>
