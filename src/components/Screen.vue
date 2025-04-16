<template>
  <div class="wrapper">

    <div class="cols">
      
      <canvas ref="experience" class="half-size-canvas"></canvas>
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
      
      <div :class="['output']">
        <p>Deviation clicked:</p>
        <div :class="['sphereconn', output.tag]">
          <p>{{ output.position }}</p>
        </div>
      </div>  
    </div>
    <hr>
    <div class="list">
      <span v-for="(sphere) in spheres" :class="['sphereconn', sphere.userData.tag]" @click="moveCamera(sphere)" >{{ sphere.position }}</span>
    </div>
  </div>
</template>

<script lang="ts">
import { onMounted, ref, shallowRef } from 'vue';
import {
  AxesHelper,
  PerspectiveCamera,
  Scene,
  WebGLRenderer,
  DirectionalLight,
  Raycaster,
  Vector2,
  Mesh,
  MeshMatcapMaterial,
  SphereGeometry,
  TextureLoader,
  Vector3,
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
      required: true
    },
    textureUrl: {
      type: String,
      required: false,
    },
  },

  setup(props) {
    const experience = ref<HTMLCanvasElement | null>(null);
    const output = shallowRef<{ position: any, tag: any }>({ position: {}, tag: {} });

    const scene = new Scene();
    const camera = new PerspectiveCamera(50, 900 / 500, 1, 1000);
    camera.position.set(50, 0, 0);  // Initial position of the camera
    camera.position.y = -30;

    const target = new Vector3(0, 0, 0);  // Initial target (center of the scene)
    let isAnimating = false;
    let animationProgress = 0;
    const animationDuration = 60;  // Frames for smooth transition

    const modelCenter = new Vector3(0, 0, 0);  // Assuming model's center at (0,0,0)
    let modelBoundingSphereRadius = 50;  // Adjust depending on your model's size

    // Directional light with shadows
    const directionalLight = new DirectionalLight(0xffffff, 1.0);
    directionalLight.position.set(10, 10, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    directionalLight.shadow.bias = -0.0005;
    scene.add(directionalLight);

    let renderer: WebGLRenderer | null = null;
    const raycaster = new Raycaster();
    const mouse = new Vector2();

    const spheres = ref<Mesh[]>([]);

    // Helper function to lerp between two vectors
    const lerp = (start: Vector3, end: Vector3, alpha: number) => {
      return start.clone().lerp(end, alpha);
    };

    // For smooth camera movement
    let initialCameraPosition = new Vector3();
    let initialLookAtPosition = new Vector3();
    let finalCameraPosition = new Vector3();
    let finalLookAtPosition = new Vector3();

    const createSpheresFromData = (data: any, scene: Scene) => {
      data.forEach((sphereInfo: any) => {
        const geometry = new SphereGeometry(
          sphereInfo.radius,
          sphereInfo.widthSegments,
          sphereInfo.heightSegments
        );
        const material = new MeshMatcapMaterial({
          color: sphereInfo.color,
          matcap: new TextureLoader().load(props.textureUrl || '')
        });
        const sphere = new Mesh(geometry, material);
        sphere.userData.tag = sphereInfo.tag;
        sphere.position.set(sphereInfo.position.x, sphereInfo.position.y, sphereInfo.position.z);
        scene.add(sphere);
        spheres.value.push(sphere);
      });
    };

    const onMouseRightClick = (event: MouseEvent) => {
      if (!renderer) return;
      
      const rect = experience.value?.getBoundingClientRect();
      if (!rect) return;

      // Convert mouse click position to normalized device coordinates
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      // Raycasting from camera to click point
      raycaster.setFromCamera(mouse, camera);

      // Intersect the model (assume the model mesh is called `model`)
      const intersects = raycaster.intersectObject(scene.children.find(c => c instanceof Mesh) as Mesh);
      
      if (intersects.length > 0) {
        const intersection = intersects[0];
        
        // Get the exact point on the surface where the ray hit the model
        const hitPoint = intersection.point;  // Vector3 with the exact hit position

        // Optionally, you can also get face and normal info
        const face = intersection.face;  // The intersected face
        const faceNormal = face?.normal;  // The normal of the face

        const tags = [
          {
            word: 'red',
            col: "#ff0000"
          },
          {
            word: 'green',
            col: "#00ff00"
          },
          {
            word: 'blue',
            col: "#0000ff"
          },
        ]
        const randomColor = tags[Math.floor(Math.random() * tags.length)];

        const snewchie = {
          "radius": 0.5,
          "widthSegments": 32,
          "heightSegments": 32,
          "color": randomColor.col,
          "tag": randomColor.word
        }

        const geometry = new SphereGeometry(
          snewchie.radius,
          snewchie.widthSegments,
          snewchie.heightSegments
        );
        const material = new MeshMatcapMaterial({
          color: snewchie.color,
          matcap: new TextureLoader().load(props.textureUrl || '')
        });
        const sphere = new Mesh(geometry, material);
        sphere.userData.tag = snewchie.tag;
        sphere.position.set(hitPoint.x, hitPoint.y, hitPoint.z);
        scene.add(sphere);
        spheres.value.push(sphere);
      }
    };

    const onMouseClick = (event: MouseEvent) => {
      if (!renderer) return;

      const rect = experience.value?.getBoundingClientRect();
      if (!rect) return;

      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(spheres.value);
      if (intersects.length > 0) {
        const sphere = intersects[0].object as Mesh;
        moveCamera(sphere);
      }
    };

    const moveCamera = (sphere: any) => {
      const spherePos = sphere.position;
        const sphereTag = sphere.userData.tag;

        output.value = { tag: sphereTag, position: spherePos};

        const spherePosition = sphere.position.clone();

        // Animate camera movement to the clicked sphere
        initialCameraPosition.copy(camera.position);  // Starting camera position
        initialLookAtPosition.copy(target);           // Starting look-at target

        // Calculate the direction from the model center to the sphere
        const direction = new Vector3()
          .subVectors(spherePosition, modelCenter)
          .normalize();

        // Adjust final camera position to be far enough away from the model and sphere
        finalLookAtPosition.copy(spherePosition);  // Look at the sphere itself
        finalCameraPosition.copy(spherePosition)
          .addScaledVector(direction, modelBoundingSphereRadius * 0.5);  // Move along the direction away from the sphere

        isAnimating = true;
        animationProgress = 0;
    }

    const toggleMarkers = (color: string) => {
      spheres.value.forEach((element) => {
        if (element.userData.tag === color) element.visible = !element.visible;
      });
    };

    onMounted(() => {
      if (experience.value) {
        renderer = new WebGLRenderer({
          canvas: experience.value,
          antialias: true,
        });
        renderer.setSize(900, 500);
        renderer.shadowMap.enabled = true;

        const controls = new OrbitControls(camera, renderer.domElement);
        controls.update();

        const animate = () => {
          requestAnimationFrame(animate);

          if (isAnimating) {
            animationProgress += 1;
            const alpha = animationProgress / animationDuration;

            // Lerp camera position and target position smoothly
            camera.position.copy(lerp(initialCameraPosition, finalCameraPosition, alpha));
            target.copy(lerp(initialLookAtPosition, finalLookAtPosition, alpha));

            // If the animation is done
            if (animationProgress >= animationDuration) {
              isAnimating = false;
            }
          }

          // Always look at the target (whether animating or not)
          camera.lookAt(target);

          controls.update();
          renderer!.render(scene, camera);
        };
        animate();

        const loader = new STLLoader();
        loader.load(
          props.modelUrl,
          (geometry) => {
            const material = new MeshMatcapMaterial({
              color: 0xcccccc,
              matcap: new TextureLoader().load(props.textureUrl || '')
            });
            const mesh = new Mesh(geometry, material);

            mesh.geometry.computeVertexNormals();
            mesh.geometry.center();

            mesh.scale.set(0.1, 0.1, 0.1);
            scene.add(mesh);

            // Add AxesHelper to show model rotation
            const axesHelper = new AxesHelper(50);  // Adjust the size if needed
            mesh.add(axesHelper);

            // Create spheres from the provided data
            createSpheresFromData(props.data, scene);

            window.addEventListener('click', onMouseClick, false);
            window.addEventListener('contextmenu', onMouseRightClick, false);
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
      moveCamera,
      experience,
      output,
      toggleMarkers,
      spheres
    };
  }
};

</script>

<style scoped>
.wrapper {
  cursor: pointer;
}
ul {
  list-style: none;
  padding: 1rem;
  li {
    margin: 1rem;
  }
}
.half-size-canvas {
  border: 1px solid black;
}
.cols {
  display: flex;
}
.output {
  width: 400px;
}
.list {
  width: 100%;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
}
.sphereconn {
  margin: 1rem;
  padding: 1rem;
  border: solid 1px;
  border-radius: 12px;
  max-width: 200px;
}
button {
  padding: 1rem;
}
.red {
  background-color: lightcoral;
}
.green {
  background-color: lightgreen;
}
.blue {
  background-color: lightblue;
}
</style>
