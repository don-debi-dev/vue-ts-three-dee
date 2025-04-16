<template>
  <div>
    <canvas ref="experience" class="half-size-canvas"></canvas>

    <div class="cols">
      <ul>
        <li>
          <button @click="toggleMarkers('red')">Toggle Red</button>
        </li>
        <li>
          <button @click="toggleMarkers('green')">Toggle Green</button>
        </li>
        <li>
          <button @click="toggleMarkers('blue')">Toggle Blue</button>
        </li>
      </ul>
      <div class="output">
        <p>Deviation clicked:</p>
        <p>{{ output }}</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { onMounted, ref, shallowRef } from 'vue';
import {
  PerspectiveCamera,
  Scene,
  WebGLRenderer,
  AmbientLight,
  DirectionalLight,
  Raycaster,
  Vector2,
  Mesh,
  MeshPhongMaterial,
  SphereGeometry,
  MeshBasicMaterial,
} from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export default {
  props: {
    modelUrl: {
      type: String,
      required: true,
    },
    lightIntensity: {
      type: Number,
      required: true,
    },
    data: {
      type: Array,
      required: false,
    },
  },

  setup(props) {
    const experience = ref<HTMLCanvasElement | null>(null);
    const output = shallowRef<string>('');

    const scene = new Scene();
    const camera = new PerspectiveCamera(75, window.innerWidth / 2 / window.innerHeight, 1, 1000);
    camera.position.z = 5;

    const ambientLight = new AmbientLight(0xffffff, props.lightIntensity);
    scene.add(ambientLight);

    const directionalLight = new DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    let renderer: WebGLRenderer | null = null;
    const raycaster = new Raycaster();
    const mouse = new Vector2();

    const spheres: Mesh[] = [];

    const createSpheresFromData = (data: any, scene: Scene) => {
      data.forEach((sphereInfo: any) => {
        const geometry = new SphereGeometry(
          sphereInfo.radius,
          sphereInfo.widthSegments,
          sphereInfo.heightSegments
        );
        const material = new MeshBasicMaterial({ color: sphereInfo.color });
        const sphere = new Mesh(geometry, material);
        sphere.userData.tag = sphereInfo.tag;
        sphere.position.set(sphereInfo.position.x, sphereInfo.position.y, sphereInfo.position.z);
        scene.add(sphere);
        spheres.push(sphere); // Add sphere to the array
      });
    };

    const onMouseClick = (event: MouseEvent) => {
      if (!renderer) return;

      const rect = experience.value?.getBoundingClientRect();
      if (!rect) return;

      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(spheres);
      if (intersects.length > 0) {
        const sphereTag = intersects[0].object.userData.tag;
        output.value = sphereTag;
        const event = new CustomEvent('deviation-clicked-event', { detail: sphereTag });
        window.document.dispatchEvent(event);
      }
    };

    const toggleMarkers = (color: string) => {
      spheres.forEach((element) => {
        if (element.userData.tag === color) element.visible = !element.visible;
      });
    };

    onMounted(() => {
      if (experience.value) {
        renderer = new WebGLRenderer({
          canvas: experience.value,
          antialias: true,
        });
        renderer.setSize(window.innerWidth / 2, window.innerHeight / 2);

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.update();

        const animate = () => {
          requestAnimationFrame(animate);
          controls.update();
          renderer!.render(scene, camera);
        };
        animate();

        const loader = new STLLoader();
        loader.load(
          props.modelUrl,
          (geometry) => {
            const material = new MeshPhongMaterial({
              color: 0x333333, // Medium gray color for metallic look
              specular: 0x999999, // Darker specular highlight
              shininess: 100, // High shininess for a metallic finish
            });
            const mesh = new Mesh(geometry, material);
            mesh.scale.set(0.1, 0.2, 0.1); // Scale down the model
            scene.add(mesh);

            // Create spheres from the provided data
            createSpheresFromData(props.data, scene);
            window.addEventListener('click', onMouseClick, false);
          },
          (xhr) => {
            console.log(`${(xhr.loaded / xhr.total) * 100}% loaded`);
          },
          (error) => {
            console.error('An error occurred while loading the STL model', error);
          }
        );
      }
    });

    return {
      experience,
      output,
      toggleMarkers,
    };
  },
};
</script>

<style scoped>
.half-size-canvas {
  width: 50vw;
  height: 50vh;
  border: 1px solid black;
}
.cols {
  display: flex;
}
.output {
  margin-left: 3rem;
}
</style>
