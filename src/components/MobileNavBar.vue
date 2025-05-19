<template>
  <nav class="mobile-nav-bar">
    <router-link to="/" class="nav-item">
      <i class="fas fa-home"></i>
      <span>首頁</span>
    </router-link>
    <router-link to="/housing" class="nav-item">
      <i class="fas fa-building"></i>
      <span>租屋列表</span>
    </router-link>
    <router-link to="/map" class="nav-item">
      <i class="fas fa-map-marker-alt"></i>
      <span>地圖搜尋</span>
    </router-link>
    <router-link to="/favorites" class="nav-item">
      <i class="fas fa-heart"></i>
      <span>我的收藏</span>
    </router-link>
    <router-link to="/sublease" class="nav-item">
      <i class="fas fa-exchange-alt"></i>
      <span>轉租專區</span>
    </router-link>
    <router-link to="/profile" class="nav-item">
      <i class="fas fa-user"></i>
      <span>個人中心</span>
    </router-link>
  </nav>
</template>

<script>
export default {
  name: 'MobileNavBar'
}
</script>

<style scoped>
.mobile-nav-bar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 0 10px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-decoration: none;
  color: #666;
  font-size: 0.8rem;
  padding: 8px 0;
  transition: all 0.3s ease;
}

.nav-item i {
  font-size: 1.2rem;
  margin-bottom: 4px;
}

.nav-item.router-link-active {
  color: var(--primary-color);
}

@media screen and (max-width: 767px) {
  .mobile-nav-bar {
    display: flex;
    justify-content: space-between;
  }
}
</style>