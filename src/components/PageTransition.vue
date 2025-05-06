<template>
  <div class="page-transition-container">
    <router-view v-slot="{ Component, route }">
      <transition 
        :name="route.meta.transition || 'fade'" 
        mode="out-in"
        @before-enter="beforeEnter"
        @enter="enter"
        @after-enter="afterEnter"
        @leave="leave"
        @after-leave="afterLeave"
      >
        <component :is="Component" :key="route.path" class="route-content" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import { useStore } from "vuex";
import { gsap } from "gsap";

export default {
  name: "PageTransition",
  setup() {
    const store = useStore();
    const currentRoute = computed(() => store.state.currentRoute);
    const isAnimating = ref(false);
    
    // 防止動畫中斷的 GSAP 動畫效果
    const beforeEnter = (el) => {
      isAnimating.value = true;
      // 完全重置元素狀態
      gsap.killTweensOf(el); // 清除任何現有的動畫
      gsap.set(el, {
        opacity: 0,
        clearProps: "", // 清除之前的屬性
      });
    };

    const enter = (el, done) => {
      // 創建新的動畫時間線，確保控制完整的動畫
      const tl = gsap.timeline({
        onComplete: () => {
          // 不要立即調用 done，等待額外的時間確保平滑過渡
          setTimeout(() => {
            done();
          }, 50);
        }
      });
      
      // 使用時間線控制動畫
      tl.to(el, {
        opacity: 1,
        duration: 0.8, // 略微增加持續時間
        ease: "power1.inOut", // 使用更平滑的緩動函數
        overwrite: "auto", // 自動處理重疊的動畫
      });
    };
    
    const afterEnter = (el) => {
      gsap.set(el, { opacity: 1 });
      setTimeout(() => {
        isAnimating.value = false;
      }, 100);
    };

    const leave = (el, done) => {
      isAnimating.value = true;
      gsap.killTweensOf(el);
      
      // 使用新的動畫時間線
      const tl = gsap.timeline({
        onComplete: () => {
          setTimeout(() => {
            done();
          }, 50);
        }
      });
      
      tl.to(el, {
        opacity: 0,
        duration: 0.7, 
        ease: "power1.inOut",
        overwrite: "auto",
      });
    };
    
    const afterLeave = (el) => {
      gsap.set(el, { opacity: 0 });
      setTimeout(() => {
        isAnimating.value = false;
      }, 100);
    };

    return {
      currentRoute,
      beforeEnter,
      enter,
      afterEnter,
      leave,
      afterLeave,
    };
  },
};
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
  will-change: opacity;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
}

/* 完全禁用 CSS 過渡，只依賴 GSAP */
.fade-enter-active,
.fade-leave-active {
  transition: none !important; /* 禁用 CSS 過渡，避免與 GSAP 衝突 */
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-active {
  position: absolute;
  width: 100%;
}

.fade-leave-active {
  position: absolute;
  width: 100%;
}
</style>