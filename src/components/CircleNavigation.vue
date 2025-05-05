<template>
    <div class="circle-navigation-container" :class="{ active: isOpen }">
      <!-- 主導航按鈕 -->
      <div class="main-nav-button" @click="toggleNavigation">
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
          @click="navigate(option.route)"
        >
          <div class="option-icon">
            <i :class="option.icon"></i>
          </div>
          <span class="option-tooltip">{{ option.label }}</span>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
  import { useStore } from 'vuex';
  import { gsap } from 'gsap';
  
  export default {
    name: 'CircleNavigation',
    setup() {
      const store = useStore();
      const isOpen = ref(false);
      
      const navOptions = [
        { label: '首頁', route: 'home', icon: 'home-icon' },
        { label: '租屋列表', route: 'accommodation-list', icon: 'list-icon' },
        { label: '地圖搜尋', route: 'map-search', icon: 'map-icon' },
        { label: '收藏', route: 'favorites', icon: 'heart-icon' },
        { label: '轉租專區', route: 'sublet', icon: 'transfer-icon' },
        { label: '個人中心', route: 'profile', icon: 'user-icon' },
      ];
      
      const toggleNavigation = () => {
        isOpen.value = !isOpen.value;
        store.commit('TOGGLE_NAVIGATION');
        
        if (isOpen.value) {
          animateNavOpen();
        } else {
          animateNavClose();
        }
      };
      
      const animateNavOpen = () => {
        gsap.to('.nav-option', {
          opacity: 1,
          scale: 1,
          stagger: 0.05,
          ease: 'back.out(1.7)',
          duration: 0.5
        });
      };
      
      const animateNavClose = () => {
        gsap.to('.nav-option', {
          opacity: 0,
          scale: 0.5,
          stagger: 0.02,
          ease: 'back.in(1.7)',
          duration: 0.3
        });
      };
      
      const getOptionStyle = (index) => {
        const totalOptions = navOptions.length;
        const angle = (index * (360 / totalOptions)) - 90;
        const radius = 80;
        
        return {
          transform: isOpen.value 
            ? `rotate(${angle}deg) translate(${radius}px) rotate(-${angle}deg)`
            : 'rotate(0deg) translate(0) rotate(0deg)',
          transition: `transform 0.5s ${index * 0.05}s cubic-bezier(0.175, 0.885, 0.32, 1.275)`
        };
      };
      
      const navigate = (route) => {
        toggleNavigation();
        store.dispatch('navigateTo', route);
      };
      
      return {
        isOpen,
        navOptions,
        toggleNavigation,
        getOptionStyle,
        navigate
      };
    }
  }
  </script>
  
  <style scoped>
  .circle-navigation-container {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
  }
  
  .main-nav-button {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #007bff, #00c6ff);
    box-shadow: 0 4px 20px rgba(0, 123, 255, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    position: relative;
    z-index: 1001;
    transition: transform 0.3s ease;
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
  }
  
  .button-icon span {
    width: 100%;
    height: 3px;
    background-color: white;
    border-radius: 3px;
    transition: all 0.3s ease;
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
    bottom: 30px;
    right: 30px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }
  
  .nav-options.visible {
    opacity: 1;
    pointer-events: all;
  }
  
  .nav-option {
    position: absolute;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    background-color: white;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0;
    scale: 0.5;
    transition: all 0.3s ease;
  }
  
  .nav-option:hover {
    background-color: #f0f8ff;
    transform: scale(1.1) !important;
  }
  
  .option-icon {
    font-size: 18px;
    color: #007bff;
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
    transition: all 0.2s ease;
    white-space: nowrap;
  }
  
  .nav-option:hover .option-tooltip {
    opacity: 1;
    visibility: visible;
  }
  </style>