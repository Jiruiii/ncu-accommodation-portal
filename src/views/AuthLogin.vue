<template>
  <div class="auth-login-redirect">
    <div class="loading">
      <div class="spinner" />
      <p>前往 Portal 認證中，請稍候…</p>
    </div>
  </div>
</template>

<script>
import apiService from "@/services/api";

export default {
  name: "AuthLogin",
  mounted() {
    // 直接導向至 Portal 授權頁
    window.location.href = apiService.auth.portal.getLoginUrl();
  },
};
</script>

<style scoped>
.auth-login-redirect {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #272727;
  color: white;
}
.loading { text-align: center; }
.spinner {
  width: 50px; height: 50px; margin: 0 auto 20px;
  border: 4px solid rgba(255,255,255,.2);
  border-radius: 50%; border-top-color: #66b3ff;
  animation: spin 1s infinite linear;
}
@keyframes spin { 0%{ transform: rotate(0) } 100%{ transform: rotate(360deg) } }
</style>
