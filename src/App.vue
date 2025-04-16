<template>
  <main class="container m-auto p-10">
    <Screen 
      :lightIntensity="1"
      :modelUrl="'../src/assets/models/Flywheel.stl'"
      :textureUrl="'../src/assets/materials/basic_1.jpg'"
      :data="deviations"
    />
  </main>
</template>

<script setup lang="ts">
import Screen from "./components/Screen.vue";
import { colors, shape, DataType } from '@/data/mock';
import { positions } from '@/data/flywheel-positions';

const deviations = new Array <DataType>;
while (deviations.length < 24) {
  const lo = {
    ...shape,
    ...colors[Math.floor(Math.random() * colors.length)],
    position: positions[Math.floor(Math.random() * positions.length)]
  }
  deviations.push(lo)
}

</script>