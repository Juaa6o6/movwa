<template>
  <v-container class="fill-height justify-center" style="max-width: 600px;">
    
    <v-col cols="12" class="text-center mb-2">
      <v-img 
        src="@/assets/logo/movwa_logo.png" 
        width="120" 
        class="mx-auto"
        alt="MOVWA Logo"
      ></v-img>
    </v-col>

    <v-window v-model="currentStep" class="w-100">
      <v-window-item :value="1">
        <SignupStep1 @next="currentStep = 2" />
      </v-window-item>

      <v-window-item :value="2">
        <SignupStep2 @next="currentStep = 3" @prev="currentStep = 1" />
      </v-window-item>

      <v-window-item :value="3">
        <SignupStep3 @prev="currentStep = 2" />
      </v-window-item>
    </v-window>

  </v-container>
</template>

<script setup>
import { ref } from 'vue'
// 분리한 컴포넌트 불러오기
import SignupStep1 from '@/components/auth/signup/SignupStep1.vue'
import SignupStep2 from '@/components/auth/signup/SignupStep2.vue'
import SignupStep3 from '@/components/auth/signup/SignupStep3.vue'

const currentStep = ref(1)
</script>