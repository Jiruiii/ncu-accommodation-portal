<template>
  <div class="comments-section">
    <h3>
      房客評論
      <span class="comment-stats" v-if="commentCount">
        <span class="avg-rating">{{ averageRating }}</span> / 5
        <span class="total-comments">({{ commentCount }} 則評論)</span>
      </span>
    </h3>

    <!-- 新增評論表單 -->
    <div class="add-comment">
      <h4>分享您的住房體驗</h4>
      <div class="rating-input">
        <span>評分：</span>
        <div class="star-rating">
          <span
            v-for="n in 5"
            :key="n"
            @click="setRating(n)"
            :class="{ active: n <= newRating }"
          >
            ★
          </span>
        </div>
      </div>
      <textarea
        v-model="commentText"
        placeholder="請分享您對這間房屋的評價、建議或經驗..."
        rows="3"
      ></textarea>
      <button
        class="submit-comment"
        @click="submitComment"
        :disabled="!commentText.trim() || !newRating || isSubmitting"
      >
        {{ isSubmitting ? "發表中..." : "發表評論" }}
      </button>
    </div>

    <!-- 載入中狀態 -->
    <div class="loading-comments" v-if="isLoading">
      <div class="loading-spinner">載入評論中...</div>
    </div>

    <!-- 評論列表 -->
    <div class="comments-list" v-else-if="comments && comments.length">
      <div v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-header">
          <div class="comment-user">
            <div class="user-avatar">
              {{ comment.userName ? comment.userName[0].toUpperCase() : "?" }}
            </div>
            <div class="user-info">
              <div class="user-name">{{ comment.userName || "匿名用戶" }}</div>
              <div class="comment-date">{{ formatDate(comment.date) }}</div>
            </div>
          </div>
          <div class="comment-rating">
            <span v-for="n in 5" :key="n" class="star">
              {{ n <= comment.rating ? "★" : "☆" }}
            </span>
          </div>
        </div>

        <div class="comment-content">{{ comment.content }}</div>

        <div class="comment-actions">
          <button
            class="like-btn"
            @click="likeComment(comment.id)"
            :disabled="isLiking"
          >
            <span class="like-icon">👍</span> {{ comment.likes }}
          </button>
        </div>
      </div>
    </div>

    <!-- 無評論時顯示 -->
    <div class="no-comments" v-else>目前還沒有評論，成為第一個評論的人吧！</div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useStore } from "vuex";

export default {
  name: "CommentSection",

  props: {
    propertyId: {
      type: [Number, String],
      required: true,
    },
  },

  setup(props) {
    const store = useStore();
    const commentText = ref("");
    const newRating = ref(0);
    const isLoading = ref(true);
    const isSubmitting = ref(false);
    const isLiking = ref(false);

    // 從 Vuex 獲取評論數據
    const comments = computed(() => {
      return store.getters.getPropertyComments(props.propertyId) || [];
    });

    // 計算平均評分
    const averageRating = computed(() => {
      return store.getters.getPropertyRating(props.propertyId);
    });

    // 計算評論數量
    const commentCount = computed(() => {
      return store.getters.getPropertyCommentCount(props.propertyId);
    });

    // 在組件掛載時從資料庫加載評論
    onMounted(async () => {
      isLoading.value = true;
      try {
        await store.dispatch("fetchPropertyComments", props.propertyId);
      } catch (error) {
        console.error("加載評論失敗:", error);
      } finally {
        isLoading.value = false;
      }
    });

    // 設置評分
    const setRating = (rating) => {
      newRating.value = rating;
    };

    // 提交評論
    const submitComment = async () => {
      if (!commentText.value.trim() || !newRating.value) return;

      isSubmitting.value = true;
      try {
        const success = await store.dispatch("addComment", {
          propertyId: props.propertyId,
          content: commentText.value.trim(),
          rating: newRating.value,
        });

        if (success) {
          // 清空表單
          commentText.value = "";
          newRating.value = 0;
        } else {
          alert("評論發佈失敗，請稍後再試");
        }
      } catch (error) {
        console.error("提交評論失敗:", error);
        alert("評論發佈失敗，請稍後再試");
      } finally {
        isSubmitting.value = false;
      }
    };

    // 點贊評論
    const likeComment = async (commentId) => {
      if (isLiking.value) return;

      isLiking.value = true;
      try {
        await store.dispatch("likeComment", {
          propertyId: props.propertyId,
          commentId,
        });
      } catch (error) {
        console.error("點贊失敗:", error);
      } finally {
        isLiking.value = false;
      }
    };

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return "未知日期";

      try {
        const date = new Date(dateString);
        return date.toLocaleDateString("zh-TW", {
          year: "numeric",
          month: "long",
          day: "numeric",
        });
      } catch (error) {
        return dateString;
      }
    };

    return {
      commentText,
      newRating,
      comments,
      averageRating,
      commentCount,
      isLoading,
      isSubmitting,
      isLiking,
      setRating,
      submitComment,
      likeComment,
      formatDate,
    };
  },
};
</script>

<style scoped>
.comments-section {
  margin-top: 25px;
  padding: 0 20px 20px;
}

.comment-stats {
  font-size: 0.9rem;
  color: #666;
  margin-left: 10px;
  font-weight: normal;
}

.avg-rating {
  color: #ff9800;
  font-weight: 600;
  font-size: 1rem;
}

.comment-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  transition: transform 0.2s;
}

.comment-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 500;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 500;
  color: #333;
}

.comment-date {
  font-size: 0.8rem;
  color: #999;
}

.comment-rating {
  color: #ff9800;
  font-size: 1.1rem;
}

.comment-content {
  color: #333;
  line-height: 1.5;
  margin: 10px 0;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
}

.like-btn {
  background: none;
  border: 1px solid #ddd;
  padding: 5px 10px;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
  color: #555;
  transition: all 0.2s;
}

.like-btn:hover:not(:disabled) {
  background: #f0f0f0;
}

.like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.like-icon {
  font-size: 1rem;
}

/* 新增評論表單 */
.add-comment {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
}

.add-comment h4 {
  margin: 0 0 15px;
  color: #333;
  font-size: 1rem;
}

.rating-input {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.star-rating {
  display: flex;
  gap: 5px;
  color: #ddd;
  font-size: 1.2rem;
  cursor: pointer;
}

.star-rating span {
  transition: color 0.2s;
}

.star-rating span:hover {
  color: #ffcc00;
}

.star-rating span.active {
  color: #ff9800;
}

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  margin-bottom: 10px;
  resize: vertical;
  font-family: inherit;
  font-size: 0.9rem;
}

.submit-comment {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.submit-comment:hover:not(:disabled) {
  background: #0069d9;
}

.submit-comment:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.no-comments {
  text-align: center;
  color: #888;
  padding: 20px;
  font-style: italic;
  background: #f9f9f9;
  border-radius: 8px;
}

.loading-comments {
  display: flex;
  justify-content: center;
  padding: 30px 0;
}

.loading-spinner {
  display: flex;
  align-items: center;
  color: #666;
}

.loading-spinner:after {
  content: "";
  width: 16px;
  height: 16px;
  margin-left: 10px;
  border: 2px solid #007bff;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .comment-header {
    flex-direction: column;
    gap: 10px;
  }

  .comment-rating {
    align-self: flex-start;
  }
}
</style>