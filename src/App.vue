<template>
  <div class="app-container">
    <PageTransition>
      <component :is="currentView" />
    </PageTransition>
    
    <CircleNavigation />
  </div>
</template>

<script>
import { computed, defineAsyncComponent, onMounted } from 'vue';
import { useStore } from 'vuex';
import CircleNavigation from '@/components/CircleNavigation.vue';
import PageTransition from '@/components/PageTransition.vue';

// 非同步載入頁面組件
const HomePage = defineAsyncComponent(() => import('@/views/HomePage.vue'));
const AccommodationList = defineAsyncComponent(() => import('@/views/AccommodationList.vue'));
const MapSearch = defineAsyncComponent(() => import('@/views/MapSearch.vue'));
const ProfilePage = defineAsyncComponent(() => import('@/views/ProfilePage.vue'));
const FavoritesPage = defineAsyncComponent(() => import('@/views/FavoritesPage.vue'));
const SubletPage = defineAsyncComponent(() => import('@/views/SubletPage.vue'));

export default {
  name: 'App',
  components: {
    CircleNavigation,
    PageTransition
  },
  setup() {
    const store = useStore();
    
    const currentView = computed(() => {
      const route = store.state.currentRoute;
      
      switch(route) {
        case 'home':
          return HomePage;
        case 'accommodation-list':
          return AccommodationList;
        case 'map-search':
          return MapSearch;
        case 'profile':
          return ProfilePage;
        case 'favorites':
          return FavoritesPage;
        case 'sublet':
          return SubletPage;
        default:
          return HomePage;
      }
    });
    
    // 初始化數據
    onMounted(() => {
      store.dispatch('fetchAccommodations');
    });
    
    return {
      currentView
    };
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

:root {
  --primary-color: #007bff;
  --secondary-color: #00c6ff;
  --accent-color: #ff6b6b;
  --text-color: #333;
  --light-gray: #f8f9fa;
  --card-shadow: 0 8px 30px rgba(0, 0, 0, 0.07);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans TC', sans-serif;
  color: var(--text-color);
  background-color: #fafafa;
  overflow-x: hidden;
}

.app-container {
  width: 100%;
  height: 100vh;
  position: relative;
}

/* 通用按鈕樣式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 30px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
}

/* 卡片樣式 */
.card {
  background-color: white;
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
}
</style>