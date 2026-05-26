<template>
  <div class="page-container">
    <CollapsableMenu v-if="$route.meta.requiresMenu" class="menu" />
    <div class="main-content">
      <router-view/>
    </div>
  </div>
</template>

<script setup>
import { CollapsableMenu } from '@/scripts/views/appView'
</script>
