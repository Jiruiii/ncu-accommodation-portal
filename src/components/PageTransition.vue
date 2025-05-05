<template>
    <div class="page-transition-container">
      <transition 
        :name="transitionName" 
        :mode="transitionMode"
        @before-enter="beforeEnter"
        @enter="enter"
        @leave="leave"
      >
        <div 
          :key="currentRoute"
          class="route-content"
        >
          <slot></slot>
        </div>
      </transition>
    </div>
  </template>
  
  <script>
  import { ref, computed, watch } from 'vue';
  import { useStore } from 'vuex';
  import { gsap } from 'gsap';
  
  export default {
    name: 'PageTransition',
    setup() {
      const store = useStore();
      const currentRoute = computed(() => store.state.currentRoute);
      const previousRoute = ref(currentRoute.value);
      const transitionName = ref('slide-left');
      const transitionMode = ref('out-in');
      
      // 路由變化策略：根據不同的路由變化應用不同的過渡效果
      const routeTransitionMap = {
        'home': {
          'accommodation-list': 'slide-left',
          'map-search': 'scale-up',
          'profile': 'slide-up',
          'favorites': 'fade',
          'default': 'slide-right'
        },
        'accommodation-list': {
          'home': 'slide-right',
          'map-search': 'fade',
          'default': 'slide-left'
        },
        'map-search': {
          'home': 'scale-down',
          'accommodation-list': 'fade',
          'default': 'slide-left'
        },
        'default': 'fade'
      };
      
      // 監聽路由變化，決定使用哪種過渡效果
      watch(currentRoute, (newRoute, oldRoute) => {
        const routeMap = routeTransitionMap[oldRoute] || routeTransitionMap['default'];
        transitionName.value = routeMap[newRoute] || routeMap['default'] || 'fade';
        previousRoute.value = oldRoute;
      });
      
      // GSAP 動畫效果
      const beforeEnter = (el) => {
        el.style.opacity = 0;
        el.style.transform = 'translateY(20px)';
      };
      
      const enter = (el, done) => {
        gsap.to(el, {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: "power2.out",
          onComplete: done
        });
      };
      
      const leave = (el, done) => {
        gsap.to(el, {
          opacity: 0,
          y: transitionName.value.includes('up') ? -20 : 
             transitionName.value.includes('down') ? 20 : 0,
          x: transitionName.value.includes('left') ? -30 : 
             transitionName.value.includes('right') ? 30 : 0,
          scale: transitionName.value.includes('scale') ? 
                 (transitionName.value.includes('up') ? 1.1 : 0.9) : 1,
          duration: 0.4,
          ease: "power2.in",
          onComplete: done
        });
      };
      
      return {
        currentRoute,
        previousRoute,
        transitionName,
        transitionMode,
        beforeEnter,
        enter,
        leave
      };
    }
  }
  </script>
  
  <style scoped>
  .page-transition-container {
    position: relative;
    width: 100%;
    height: 100vh;
    overflow: hidden;
  }
  
  .route-content {
    position: absolute;
    width: 100%;
    height: 100%;
  }
  
  /* 基本淡入淡出效果 */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.5s ease;
  }
  
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
  }
  
  /* 其他過渡效果使用 GSAP 來實現 */
  </style>