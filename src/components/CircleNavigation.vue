<template>
  <div class="circle-navigation-wrapper">
    <div
      class="circle-navigation-container"
      :class="{ active: isOpen, dragging: isDragging }"
      ref="navContainer"
      :style="positionStyle"
      @mousedown.stop="handleCircleMouseDown"
      @touchstart.stop="handleCircleTouchStart"
    >
      <!-- 拖動提示 -->
      <div
        class="drag-handle"
        v-show="isOpen"
        @mousedown.stop="startDragWhenOpen"
        @touchstart.stop="startDragWhenOpen"
      >
        <span class="drag-icon">⋮⋮</span>
        <span>拖動</span>
        <span class="drag-icon">⋮⋮</span>
      </div>

      <!-- 主導航按鈕 -->
      <div
        class="main-nav-button"
        @click.stop="handleMainButtonClick"
        @mousedown.stop="handleMainButtonMouseDown"
        @touchstart.stop="handleMainButtonTouchStart"
      >
        <div class="button-icon" :class="{ 'is-open': isOpen }">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <!-- 導航選項 -->
      <div class="nav-options" :class="{ visible: isOpen }">
        <div
          v-for="(option, index) in navOptions"
          :key="option.route"
          class="nav-option"
          :style="getOptionStyle(index)"
          @click.stop.prevent="navigate(option.route)"
        >
          <div class="option-icon">
            <i :class="option.icon"></i>
          </div>
          <span class="option-tooltip" :class="getTooltipClass()">
            {{ option.label }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  /* eslint-disable */
  import { ref, onMounted, onBeforeUnmount, computed, nextTick } from "vue";
  import { useStore } from "vuex";
  import { gsap } from "gsap";

  export default {
    name: "CircleNavigation",
    setup() {
      const store = useStore();
      const isOpen = ref(false);
      const isAnimating = ref(false);
      const navContainer = ref(null);

      // 使用 ref 直接控制位置，而不是操作 DOM
      const positionX = ref(0);
      const positionY = ref(0);

      // 計算樣式
      const positionStyle = computed(() => {
        return {
          transform: `translate(${positionX.value}px, ${positionY.value}px)`,
        };
      });

      // 拖動相關變數
      const isDragging = ref(false);
      const dragOffsetX = ref(0);
      const dragOffsetY = ref(0);

      // 紀錄拖拉相關變數
      const dragStartTime = ref(0);
      const hasDragged = ref(false);
      const clickThreshold = 500; // 拖動閾值

      // 屏幕位置
      const screenPosition = ref({
        isRight: true,
        isBottom: true,
      });

      // 導航選項
      const navOptions = [
        { label: "首頁", route: "home", icon: "home-icon" },
        { label: "租屋列表", route: "accommodation-list", icon: "list-icon" },
        { label: "地圖搜尋", route: "map-search", icon: "map-icon" },
        { label: "收藏", route: "favorites", icon: "heart-icon" },
        { label: "轉租專區", route: "sublet", icon: "transfer-icon" },
        { label: "個人中心", route: "profile", icon: "user-icon" },
      ];

      // 初始化動畫時間線
      let tl = null;

      onMounted(() => {
        // 預設將所有選項設為隱藏
        gsap.set(".nav-option", {
          opacity: 0,
          scale: 0.5,
          x: 0,
          y: 0,
        });

        // 設置為右下角
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        // 右下角位置，留出距離
        positionX.value = windowWidth - 90;
        positionY.value = windowHeight - 90;

        // 添加全局事件監聽器
        document.addEventListener("mousemove", handleMouseMove);
        document.addEventListener("mouseup", handleMouseUp);
        document.addEventListener("touchmove", handleTouchMove, {
          passive: false,
        });
        document.addEventListener("touchend", handleTouchEnd);
        window.addEventListener("resize", handleResize);
      });

      onBeforeUnmount(() => {
        // 清除事件監聽器
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
        document.removeEventListener("touchmove", handleTouchMove);
        document.removeEventListener("touchend", handleTouchEnd);
        window.removeEventListener("resize", handleResize);
      });

      // 處理窗口大小變化
      const handleResize = () => {
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        // 確保元素保持在視窗內
        positionX.value = Math.min(positionX.value, windowWidth - 90);
        positionY.value = Math.min(positionY.value, windowHeight - 90);

        // 如果導航是打開的，重新計算展開位置
        if (isOpen.value) {
          setTimeout(animateNavOpen, 50);
        }
      };

      // 當未展開時拖動
      const startDrag = (event) => {
        // 如果點擊的是主按鈕，不啟動拖曳
        if (event.target.closest(".main-nav-button")) {
          return;
        }

        isDragging.value = true;

        // 獲取當前元素位置
        const rect = navContainer.value.getBoundingClientRect();

        // 計算鼠標在元素內的相對位置
        if (event.type.startsWith("mouse")) {
          dragOffsetX.value = event.clientX - rect.left;
          dragOffsetY.value = event.clientY - rect.top;
        } else if (event.type.startsWith("touch")) {
          const touch = event.touches[0];
          dragOffsetX.value = touch.clientX - rect.left;
          dragOffsetY.value = touch.clientY - rect.top;
        }
      };

      // 當展開時拖動
      const startDragWhenOpen = (event) => {
        event.preventDefault();
        event.stopPropagation();

        isDragging.value = true;

        // 獲取當前元素位置
        const rect = navContainer.value.getBoundingClientRect();

        // 計算鼠標在元素內的相對位置
        if (event.type.startsWith("mouse")) {
          dragOffsetX.value = event.clientX - rect.left;
          dragOffsetY.value = event.clientY - rect.top;
        } else if (event.type.startsWith("touch")) {
          const touch = event.touches[0];
          dragOffsetX.value = touch.clientX - rect.left;
          dragOffsetY.value = touch.clientY - rect.top;
        }
      };

      // 鼠標拖動
      const handleMouseMove = (event) => {
        if (!isDragging.value) return;

        event.preventDefault();

        hasDragged.value = true; // 標記為拖拉狀態

        updatePosition(event.clientX, event.clientY);
      };

      // 觸摸拖動
      const handleTouchMove = (event) => {
        if (!isDragging.value) return;

        event.preventDefault();

        hasDragged.value = true; // 標記為拖拉狀態

        const touch = event.touches[0];
        updatePosition(touch.clientX, touch.clientY);
      };

      // 更新位置
      const updatePosition = (clientX, clientY) => {
        const x = clientX - dragOffsetX.value;
        const y = clientY - dragOffsetY.value;

        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        const width = isOpen.value ? 250 : 60;
        const height = isOpen.value ? 250 : 60;

        // 確保不超出視窗範圍
        positionX.value = Math.min(Math.max(0, x), windowWidth - width);
        positionY.value = Math.min(Math.max(0, y), windowHeight - height);

        // 更新屏幕位置標記
        screenPosition.value = {
          isRight: positionX.value > windowWidth / 2,
          isBottom: positionY.value > windowHeight / 2,
        };
      };

      // 拖動結束
      const handleMouseUp = (event) => {
        if (isDragging.value) {
          isDragging.value = false;

          const isClick =
            new Date().getTime() - dragStartTime.value < clickThreshold &&
            !hasDragged.value;

          // 如果不是點擊，立即重置狀態，避免誤觸發點擊事件
          if (!isClick) {
            event.preventDefault();
            event.stopPropagation();
          }

          if (isOpen.value) {
            // 確保選項位置正確
            setTimeout(animateNavOpen, 50);
          }

          setTimeout(() => {
            hasDragged.value = false;
          }, 100);
        }
      };

      const handleTouchEnd = handleMouseUp;

      // 切換導航 - 優化重置邏輯
      const toggleNavigation = () => {
        if (isAnimating.value) return;

        isAnimating.value = true;

        // 在改變狀態前記錄當前主按鈕位置
        const mainButton = navContainer.value.querySelector(".main-nav-button");
        const buttonRect = mainButton.getBoundingClientRect();
        const oldButtonRight = buttonRect.right;
        const oldButtonBottom = buttonRect.bottom;

        // 改變展開狀態
        isOpen.value = !isOpen.value;

        // 根據狀態更新容器類
        if (isOpen.value) {
          navContainer.value.classList.add("active");
          navContainer.value.classList.remove("closing");
        } else {
          navContainer.value.classList.remove("active");
          navContainer.value.classList.add("closing");

          // 收起時隱藏所有提示
          document.querySelectorAll(".option-tooltip").forEach((tooltip) => {
            tooltip.style.opacity = "0";
            tooltip.style.visibility = "hidden";
            tooltip.style.display = "none";
          });
        }

        // 狀態變化後需要調整位置以保持主按鈕位置不變
        nextTick(() => {
          // 重新獲取按鈕位置
          const newRect = mainButton.getBoundingClientRect();
          // 計算位置差異
          const deltaX = newRect.right - oldButtonRight;
          const deltaY = newRect.bottom - oldButtonBottom;

          // 調整容器位置以保持主按鈕在原位
          positionX.value -= deltaX;
          positionY.value -= deltaY;

          // 根據狀態執行動畫
          if (isOpen.value) {
            animateNavOpen();
          } else {
            navContainer.value.classList.add("animating");
            animateNavClose();
          }

          // 設置足夠的動畫時間
          const animationDuration = isOpen.value
            ? 600
            : navOptions.length * 50 + 300;

          setTimeout(() => {
            // 重要：確保動畫結束後移除所有臨時類
            isAnimating.value = false;
            navContainer.value.classList.remove("closing");
            navContainer.value.classList.remove("animating");
          }, animationDuration);
        });
      };

      const handleCircleMouseDown = (event) => {
        // 如果點擊到主按鈕，則不啟動拖拉
        if (
          event.target.closest(".main-nav-button") ||
          (isOpen.value && !event.target.closest(".drag-handle"))
        ) {
          return;
        }

        // 開始拖拉
        isDragging.value = true;

        // 獲取當前元素位置
        const rect = navContainer.value.getBoundingClientRect();

        // 計算鼠標在元素內的相對位置
        dragOffsetX.value = event.clientX - rect.left;
        dragOffsetY.value = event.clientY - rect.top;
      };

      const handleCircleTouchStart = (event) => {
        // 如果點擊到主按鈕，則不啟動拖拉
        if (
          event.target.closest(".main-nav-button") ||
          (isOpen.value && !event.target.closest(".drag-handle"))
        ) {
          return;
        }

        // 開始拖拉
        isDragging.value = true;

        // 獲取當前元素位置
        const rect = navContainer.value.getBoundingClientRect();

        // 計算觸摸點在元素內的相對位置
        const touch = event.touches[0];
        dragOffsetX.value = touch.clientX - rect.left;
        dragOffsetY.value = touch.clientY - rect.top;
      };

      // 展開動畫 - 確保每次都能正常展開
      const animateNavOpen = () => {
        if (tl) tl.kill();

        // 獲取選項元素
        const navOptionElements = document.querySelectorAll(".nav-option");
        if (!navOptionElements.length) return;

        // 確保所有元素的初始狀態正確
        navOptionElements.forEach((elem) => {
          elem.style.visibility = "visible";
          elem.style.display = "flex";

          // 重要：確保從原點開始
          gsap.set(elem, {
            x: 0,
            y: 0,
            opacity: 0,
            scale: 0.5,
          });
        });

        // 創建時間線
        tl = gsap.timeline();

        // 獲取展開方向
        const windowWidth = window.innerWidth;
        const windowHeight = window.innerHeight;

        // 容器中心點在視窗中的位置
        const mainButton = navContainer.value.querySelector(".main-nav-button");
        const buttonRect = mainButton.getBoundingClientRect();
        const buttonCenterX = buttonRect.left + buttonRect.width / 2;
        const buttonCenterY = buttonRect.top + buttonRect.height / 2;

        // 確定展開方向
        const expandRight = buttonCenterX < windowWidth / 2;
        const expandDown = buttonCenterY < windowHeight / 2;

        // 計算每個選項位置
        navOptionElements.forEach((elem, index) => {
          // 計算選項位置
          let angle;
          const totalOptions = navOptions.length;

          // 根據位置計算角度範圍
          let startAngle, endAngle;

          if (expandRight && expandDown) {
            startAngle = 0;
            endAngle = 180;
          } else if (expandRight && !expandDown) {
            startAngle = 180;
            endAngle = 360;
          } else if (!expandRight && expandDown) {
            startAngle = 0;
            endAngle = 180;
          } else {
            startAngle = 180;
            endAngle = 360;
          }

          angle =
            startAngle + (index / (totalOptions - 1)) * (endAngle - startAngle);
          const radians = (angle * Math.PI) / 180;

          const radius = 110;
          const x = Math.cos(radians) * radius;
          const y = Math.sin(radians) * radius;

          // 從原點到最終位置的動畫
          tl.to(
            elem,
            {
              x: x,
              y: y,
              opacity: 1,
              scale: 1,
              duration: 0.5,
              delay: index * 0.05,
              ease: "back.out(1.7)",
              overwrite: "auto",
            },
            0
          );
        });
      };

      // 收起動畫 - 終極修正版
      const animateNavClose = () => {
        // 清除前一個動畫
        if (tl) tl.kill();

        // 標記為正在動畫中
        navContainer.value.classList.add("animating");

        // 獲取當前所有可見的選項元素
        const navOptionElements = Array.from(
          document.querySelectorAll(".nav-option")
        );
        if (navOptionElements.length === 0) return;

        // 創建單獨的 GSAP 動畫，不使用時間線
        // 按照原始數組的倒序處理元素
        [...navOptionElements].reverse().forEach((elem, index) => {
          // 使用 GSAP 獲取當前位置
          const currentX = gsap.getProperty(elem, "x") || 0;
          const currentY = gsap.getProperty(elem, "y") || 0;

          // 確保元素可見且處於正確的初始位置
          gsap.set(elem, {
            x: currentX,
            y: currentY,
            opacity: 1,
            scale: 1,
            visibility: "visible",
            display: "flex",
          });

          // 使用延遲創建收起序列
          const delay = index * 0.07;

          // 單獨創建動畫
          gsap.to(elem, {
            x: 0,
            y: 0,
            opacity: 0,
            scale: 0.5,
            duration: 0.5,
            delay: delay,
            ease: "back.in(1.7)",
            onStart: function () {
              console.log(
                `元素 ${navOptionElements.length - 1 - index} 開始收起動畫`
              );
            },
            onComplete: function () {
              // 動畫結束時隱藏元素
              elem.style.visibility = "hidden";
              elem.style.display = "none";

              // 如果是最後一個元素，進行最終清理
              if (index === navOptionElements.length - 1) {
                // 確保所有元素都重置到初始狀態
                navOptionElements.forEach((el) => {
                  gsap.set(el, {
                    clearProps: "all",
                    x: 0,
                    y: 0,
                    opacity: 0,
                    scale: 0.5,
                    visibility: "hidden",
                    display: "none",
                  });
                });

                // 移除動畫標記
                navContainer.value.classList.remove("animating");
                console.log("所有收起動畫完成");
              }
            },
          });
        });
      };

      // 根據屏幕位置調整工具提示的位置
      const getTooltipClass = () => {
        const positions = [];

        if (!screenPosition.value.isRight) {
          positions.push("tooltip-left");
        }

        if (!screenPosition.value.isBottom) {
          positions.push("tooltip-top");
        }

        return positions;
      };

      const getOptionStyle = (index) => {
        return {
          transitionDelay: `${index * 0.05}s`,
        };
      };

      const navigate = (route) => {
        toggleNavigation();

        if (store && typeof store.dispatch === "function") {
          try {
            store.dispatch("navigateTo", route);
          } catch (e) {
            console.error("無法導航到", route, e);
          }
        }
      };

      // 處理主按鈕點擊
      const handleMainButtonClick = (event) => {
        event.preventDefault();
        // 如果是拖拉結束後，不觸發點擊事件
        if (hasDragged.value) {
          return;
        }

        // 如果滿足點擊條件（時間短且沒有明顯位移），才切換導航
        if (new Date().getTime() - dragStartTime.value < clickThreshold) {
          toggleNavigation();
        }
      };

      // 處理主按鈕的鼠標按下事件
      const handleMainButtonMouseDown = (event) => {
        event.stopPropagation();

        // 記錄開始時間和狀態
        dragStartTime.value = new Date().getTime();
        hasDragged.value = false;

        // 獲取當前元素位置
        const rect = navContainer.value.getBoundingClientRect();

        // 計算鼠標在元素內的相對位置
        dragOffsetX.value = event.clientX - rect.left;
        dragOffsetY.value = event.clientY - rect.top;

        // 立即標記為拖拉狀態
        isDragging.value = true;
      };

      // 處理主按鈕的觸摸開始事件
      const handleMainButtonTouchStart = (event) => {
        event.stopPropagation();

        // 記錄開始時間和狀態
        dragStartTime.value = new Date().getTime();
        hasDragged.value = false;

        // 獲取當前元素位置
        const rect = navContainer.value.getBoundingClientRect();

        // 計算觸摸點在元素內的相對位置
        const touch = event.touches[0];
        dragOffsetX.value = touch.clientX - rect.left;
        dragOffsetY.value = touch.clientY - rect.top;

        // 立即標記為拖拉狀態
        isDragging.value = true;
      };

      return {
        isOpen,
        navOptions,
        navContainer,
        isDragging,
        positionStyle,
        toggleNavigation,
        getOptionStyle,
        getTooltipClass,
        navigate,
        startDrag,
        startDragWhenOpen,
        handleCircleMouseDown,
        handleCircleTouchStart,
        handleMainButtonClick,
        handleMainButtonMouseDown,
        handleMainButtonTouchStart,
      };
    },
  };
</script>

<style scoped>
  .circle-navigation-wrapper {
    position: fixed;
    z-index: 1000;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    transform-origin: bottom right;
    will-change: transform, width, height;
  }

  .circle-navigation-container {
    position: absolute;
    z-index: 1000;
    width: 60px;
    height: 60px;
    pointer-events: auto;
    user-select: none;
    touch-action: none;
  }

  .circle-navigation-container.dragging {
    opacity: 0.95;
    box-shadow: 0 8px 30px rgba(0, 123, 255, 0.6);
    cursor: move !important;
  }

  .circle-navigation-container.dragging .main-nav-button {
    cursor: move;
    box-shadow: 0 4px 25px rgba(0, 123, 255, 0.7);
    transform: scale(1.05);
  }

  .circle-navigation-container.active {
    width: 250px;
    height: 250px;
  }

  .circle-navigation-container:not(.active) .option-tooltip,
  .animating .option-tooltip {
    opacity: 0 !important;
    visibility: hidden !important;
    display: none !important;
    pointer-events: none !important;
    transition: none !important;
  }

  /* 動畫中禁用所有過渡效果 */
  .animating .nav-option {
    transition: none !important;
  }

  .container-drag-area {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    cursor: move;
    z-index: 1000;
  }

  .drag-handle {
    position: absolute;
    top: -25px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.75);
    color: white;
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 12px;
    opacity: 0.9;
    cursor: move;
    pointer-events: auto;
    z-index: 1005;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    user-select: none;
    white-space: nowrap;
  }

  .drag-handle:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.9);
  }

  .drag-icon {
    display: inline-block;
    margin: 0 4px;
    transform: rotate(90deg);
  }

  .main-nav-button {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #007bff, #00c6ff);
    box-shadow: 0 4px 20px rgba(0, 123, 255, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 1001;
    user-select: none;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    will-change: transform;
  }

  .main-nav-button:hover {
    transform: scale(1.05);
  }

  .button-icon {
    width: 24px;
    height: 24px;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    pointer-events: none;
  }

  .button-icon span {
    width: 100%;
    height: 3px;
    background-color: white;
    border-radius: 3px;
    transition: all 0.3s ease;
    pointer-events: none;
  }

  .button-icon.is-open span:nth-child(1) {
    transform: rotate(45deg) translate(5px, 8px);
  }

  .button-icon.is-open span:nth-child(2) {
    opacity: 0;
  }

  .button-icon.is-open span:nth-child(3) {
    transform: rotate(-45deg) translate(5px, -8px);
  }

  .nav-options {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 250px;
    height: 250px;
    pointer-events: none;
    z-index: 999;
    visibility: hidden;
  }

  .nav-options.visible {
    pointer-events: auto;
    visibility: visible;
  }

  .nav-option {
    position: absolute;
    bottom: 7px;
    right: 7px;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background-color: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0;
    transform: scale(0.5);
    z-index: 999;
    user-select: none;
    transition: background-color 0.2s ease;
  }

  .nav-option:hover {
    background-color: #f0f8ff;
    transform: scale(1.1) !important;
  }

  .option-icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #007bff;
    pointer-events: none;
  }

  /* 圖標樣式 */
  .home-icon,
  .list-icon,
  .map-icon,
  .heart-icon,
  .transfer-icon,
  .user-icon {
    width: 100%;
    height: 100%;
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
    pointer-events: none;
  }

  .home-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23007bff"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>');
  }

  .list-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23007bff"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/></svg>');
  }

  .map-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23007bff"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/></svg>');
  }

  .heart-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23007bff"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>');
  }

  .transfer-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23007bff"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>');
  }

  .user-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23007bff"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>');
  }

  .option-tooltip {
    position: absolute;
    background-color: #333;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    visibility: hidden;
    display: none;
    transition: opacity 0.2s ease, visibility 0.2s ease;
    white-space: nowrap;
    z-index: 1010;
    pointer-events: none;
  }

  .nav-options.visible .nav-option:hover .option-tooltip {
    opacity: 1;
    visibility: visible;
    display: block;
  }

  .option-tooltip.tooltip-left {
    left: auto;
    right: 125%;
    bottom: 50%;
    transform: translateY(50%);
  }

  .option-tooltip.tooltip-top {
    bottom: auto;
    top: 125%;
  }

  .nav-option:hover .option-tooltip {
    opacity: 1;
    visibility: visible;
  }

  /* 添加箭頭 */
  .option-tooltip:after {
    content: "";
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #333;
    pointer-events: none;
  }

  .option-tooltip.tooltip-left:after {
    left: auto;
    right: -10px;
    bottom: 50%;
    transform: translateY(50%);
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-left: 5px solid #333;
    border-right: none;
  }

  .option-tooltip.tooltip-top:after {
    bottom: auto;
    top: -5px;
    transform: translateX(-50%) rotate(180deg);
  }

  /* 處理收起動畫期間的狀態 */
  .closing .nav-options {
    visibility: visible !important;
  }

  /* 確保動畫中的元素具有更高優先級 */
  .circle-navigation-container .nav-option {
    will-change: transform, opacity, scale;
  }

  /* 確保收起過程中的元素可見但工具提示隱藏 */
  .closing .nav-option {
    pointer-events: none !important;
  }

  .closing .option-tooltip,
  .circle-navigation-container:not(.active) .option-tooltip {
    opacity: 0 !important;
    visibility: hidden !important;
    display: none !important;
  }

  @media (max-width: 768px) {
    .circle-navigation-container.active {
      width: 220px;
      height: 220px;
    }

    .nav-options {
      width: 220px;
      height: 220px;
    }

    .nav-option {
      width: 40px;
      height: 40px;
    }

    .option-tooltip {
      font-size: 11px;
      padding: 4px 8px;
    }
  }
</style>
