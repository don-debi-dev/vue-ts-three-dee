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
  SphereGeometry,
  Mesh,
  MeshBasicMaterial,
  Raycaster,
  Vector2
} from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
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
    const camera = new PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 1000);
    camera.position.z = 5;

    const ambientLight = new AmbientLight(0xffffff, props.lightIntensity); // Use the prop for light intensity
    scene.add(ambientLight);

    let renderer: WebGLRenderer | null = null;
    const raycaster = new Raycaster();
    const mouse = new Vector2();

    const spheres: Mesh[] = []; // Array to hold all sphere meshes

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

      raycaster.ray.origin.setFromMatrixPosition(camera.matrixWorld);
      raycaster.ray.direction
        .set(mouse.x, mouse.y, 1)
        .unproject(camera)
        .sub(raycaster.ray.origin)
        .normalize();

      const intersects = raycaster.intersectObjects(spheres);
      if (intersects.length > 0) {
        const sphereTag = intersects[0].object.userData.tag;
        output.value = sphereTag;
        const event = new CustomEvent('deviation-clicked-event', { detail: sphereTag })
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
        camera.position.set(0, 16, 0);
        controls.update();

        const animate = () => {
          requestAnimationFrame(animate);
          controls.update();
          renderer!.render(scene, camera);
        };
        animate();

        const loader = new GLTFLoader();
        loader.load(
          props.modelUrl,
          (gltf) => {
            gltf.scene.position.y = -2;
            scene.add(gltf.scene);
            createSpheresFromData(props.data, scene);
            window.addEventListener('click', onMouseClick, false);
          },
          (xhr) => {
            // console.log(`${(xhr.loaded / xhr.total) * 100}% loaded`);
          },
          (error) => {
            console.error('An error happened while loading the GLTF model', error);
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
  :last-child {
    margin-left: 3rem;
  }
}
</style>
