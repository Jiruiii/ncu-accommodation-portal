<template>
    <div class="not-found">
        <div class="container">
            <div class="error-content">
                <h1 class="error-code">404</h1>
                <div class="divider"></div>
                <h2 class="error-message">頁面不存在</h2>
                <p class="error-description">
                    您要尋找的頁面可能已被移除、名稱變更，或暫時無法使用。
                </p>
                <router-link to="/" class="home-button">
                    <span>返回首頁</span>
                    <i class="fas fa-arrow-right"></i>
                </router-link>
            </div>
            <!-- <div class="illustration">
                <img src="@/assets/house-not-found.svg" alt="House not found" 
                        onerror="this.onerror=null; this.src='https://cdn-icons-png.flaticon.com/512/6134/6134065.png';" />
            </div> -->
        </div>
    </div>
</template>

<script>
export default {
    name: "NotFound"
};
</script>

<style scoped>
.not-found {
    min-height: calc(100vh - 80px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background-color: #f9f9f9;
}

.container {
    max-width: 1200px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 3rem;
    padding: 3rem;
    border-radius: 12px;
    background-color: white;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

.error-content {
    flex: 1;
    padding: 1rem;
}

.error-code {
    font-size: 8rem;
    font-weight: 700;
    color: #2c3e50;
    line-height: 1;
    margin: 0;
    opacity: 0.8;
}

.divider {
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, #42b883, #35495e);
    margin: 20px 0;
    border-radius: 2px;
}

.error-message {
    font-size: 2.5rem;
    font-weight: 600;
    color: #2c3e50;
    margin: 0.5rem 0;
}

.error-description {
    font-size: 1.1rem;
    color: #5c6b7a;
    margin: 1rem 0 2rem;
    line-height: 1.6;
}

.home-button {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.8rem 1.5rem;
    background: linear-gradient(90deg, #42b883, #35495e);
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 10px rgba(66, 184, 131, 0.25);
}

.home-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(66, 184, 131, 0.35);
}

.illustration {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.illustration img {
    max-width: 100%;
    height: auto;
    max-height: 300px;
}

@media (max-width: 900px) {
    .container {
        flex-direction: column-reverse;
        padding: 2rem;
        gap: 2rem;
    }
    
    .error-code {
        font-size: 5rem;
    }
    
    .error-message {
        font-size: 2rem;
    }
}
</style>