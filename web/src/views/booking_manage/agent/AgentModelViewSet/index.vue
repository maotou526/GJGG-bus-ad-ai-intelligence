<!--
 * @Description: 代理商管理
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
-->
<template>
    <BookingAgentsPage />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import BookingAgentsPage from './BookingAgentsPage.vue';

export default defineComponent({
    name: "AgentModelViewSet",
    components: {
        BookingAgentsPage
    }
});
</script>

<style scoped> 
</style>
