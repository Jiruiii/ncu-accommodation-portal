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
    <div class="add-comment" v-if="isLoggedIn">
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
    <div class="login-prompt" v-else>
      <p>請先登入以分享您的住房體驗</p>
      <button @click="redirectToLogin" class="login-btn">前往登入</button>
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
          <div class="comment-actions-top">
            <div class="comment-rating">
              <span v-for="n in 5" :key="n" class="star">
                {{ n <= comment.rating ? "★" : "☆" }}
              </span>
              <div class="comment-options">
                <button
                  v-if="canEditComment(comment)"
                  class="edit-btn"
                  @click="startEditComment(comment)"
                  title="編輯評論"
                >
                  <i class="material-icons">edit</i>
                </button>
                <button
                  v-if="canDeleteComment(comment)"
                  class="delete-btn"
                  @click="confirmDeleteComment(comment.id)"
                  title="刪除評論"
                >
                  <i class="material-icons">delete</i>
                </button>
                <button
                  v-if="!canEditComment(comment)"
                  class="report-btn"
                  @click="openReportModal('comment', comment.id)"
                  title="舉報評論"
                >
                  <i class="material-icons">flag</i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="comment-content" v-if="editingCommentId !== comment.id">
          {{ comment.content }}
        </div>

        <!-- 評論內容區塊增加編輯功能 -->
        <div v-if="editingCommentId === comment.id" class="edit-comment-form">
          <textarea
            v-model="editCommentText"
            rows="3"
            placeholder="編輯您的評論..."
          ></textarea>
          <div class="rating-input">
            <span>評分：</span>
            <div class="star-rating">
              <span
                v-for="n in 5"
                :key="n"
                @click="setEditRating(n)"
                :class="{ active: n <= editRating }"
              >
                ★
              </span>
            </div>
          </div>
          <div class="edit-actions">
            <button @click="cancelEditComment" class="cancel-edit-btn">
              取消
            </button>
            <button
              @click="updateComment(comment.id)"
              class="update-comment-btn"
              :disabled="!editCommentText.trim() || !editRating"
            >
              更新評論
            </button>
          </div>
        </div>

        <div class="comment-actions">
          <button
            class="like-btn"
            @click="likeComment(comment.id)"
            :disabled="isLiking"
            :class="{ liked: isCommentLiked(comment) }"
          >
            <span class="like-icon"
              ><svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                width="16"
                height="16"
                fill="currentColor"
              >
                <path
                  d="M12,21.35L10.55,20.03C5.4,15.36 2,12.27 2,8.5C2,5.41 4.42,3 7.5,3C9.24,3 10.91,3.81 12,5.08C13.09,3.81 14.76,3 16.5,3C19.58,3 22,5.41 22,8.5C22,12.27 18.6,15.36 13.45,20.03L12,21.35Z"
                /></svg
            ></span>
            <span>{{
              typeof comment.likes === "number" ? comment.likes : 0
            }}</span>
          </button>
          <button class="reply-btn" @click="showReplyForm(comment.id)">
            回覆 ({{ comment.replyCount || 0 }})
          </button>
        </div>

        <!-- 回覆表單 -->
        <div class="reply-form" v-if="replyingToId === comment.id">
          <textarea
            v-model="replyText"
            placeholder="輸入您的回覆..."
            rows="2"
          ></textarea>
          <div class="reply-actions">
            <button @click="cancelReply" class="cancel-reply-btn">取消</button>
            <button
              @click="submitReply(comment.id)"
              class="submit-reply-btn"
              :disabled="!replyText.trim() || isSubmittingReply"
            >
              {{ isSubmittingReply ? "發送中..." : "發送回覆" }}
            </button>
          </div>
        </div>

        <!-- 回覆列表 -->
        <div class="replies-list" v-if="showingRepliesForId === comment.id">
          <div v-if="isLoadingReplies" class="loading-replies">
            <div class="loading-spinner">載入回覆中...</div>
          </div>

            <div v-else-if="replies.length > 0" class="replies-container">
              <div v-for="reply in replies" :key="reply.id" class="reply-item">
                <div class="reply-header">
                  <div class="reply-user">
                    <div class="user-avatar small">
                      {{ reply.author ? reply.author[0].toUpperCase() : "?" }}
                    </div>
                    <div class="user-info">
                      <div class="user-name">
                        {{ reply.author || "匿名用戶" }}
                      </div>
                      <div class="reply-date">
                        {{ formatDate(reply.created_at) }}
                      </div>
                    </div>
                  </div>
                  <div class="reply-options">
                    <button
                      v-if="canEditReply(reply)"
                      class="edit-btn small"
                      @click="startEditReply(reply)"
                      title="編輯回覆"
                    >
                      <i class="material-icons">edit</i>
                    </button>
                    <button
                      v-if="canDeleteReply(reply)"
                      class="delete-btn small"
                      @click="confirmDeleteReply(reply.id)"
                      title="刪除回覆"
                    >
                      <i class="material-icons">delete</i>
                    </button>
                    <button
                      v-if="!canEditReply(reply)"
                      class="report-btn small"
                      @click="openReportModal('reply', reply.id)"
                      title="舉報回覆"
                    >
                      <i class="material-icons">flag</i>
                    </button>
                  </div>
                </div>
                <div v-if="editingReplyId === reply.id" class="edit-reply-form">
                  <textarea
                    v-model="editReplyText"
                    rows="2"
                    placeholder="編輯您的回覆..."
                  ></textarea>
                  <div class="edit-actions">
                    <button @click="cancelEditReply" class="cancel-edit-btn">
                      取消
                    </button>
                    <button
                      @click="updateReply(reply.id)"
                      class="update-reply-btn"
                      :disabled="!editReplyText.trim()"
                    >
                      更新回覆
                    </button>
                  </div>
                </div>
                <div v-else class="reply-content">{{ reply.content }}</div>
                <div class="reply-actions">
                  <button
                    class="like-btn small"
                    @click="likeReply(reply.id)"
                    :disabled="isReplyLiking"
                    :class="{ liked: isReplyLiked(reply) }"
                  >
                    <span class="like-icon"
                      ><svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        width="16"
                        height="16"
                        fill="currentColor"
                      >
                        <path
                          d="M12,21.35L10.55,20.03C5.4,15.36 2,12.27 2,8.5C2,5.41 4.42,3 7.5,3C9.24,3 10.91,3.81 12,5.08C13.09,3.81 14.76,3 16.5,3C19.58,3 22,5.41 22,8.5C22,12.27 18.6,15.36 13.45,20.03L12,21.35Z"
                        /></svg
                    ></span>
                    <span>{{
                      Array.isArray(reply.likes) ? reply.likes.length : 0
                    }}</span>
                  </button>
                </div>
              </div>
            </div>

          <div v-else class="no-replies">目前沒有回覆</div>

          <button class="hide-replies-btn" @click="hideReplies">
            收起回覆
          </button>
        </div>

        <button
          v-if="!showingRepliesForId && comment.replyCount > 0"
          class="show-replies-btn"
          @click="showReplies(comment.id)"
        >
          顯示 {{ comment.replyCount }} 則回覆
        </button>
      </div>
    </div>

    <!-- 無評論時顯示 -->
    <transition name="fade">
      <div
        class="no-comments"
        v-if="!isLoading && (!comments || !comments.length)"
      >
        目前還沒有評論，成為第一個評論的人吧！
      </div>
    </transition>

    <div class="delete-modal" v-if="showDeleteModal">
      <div class="delete-modal-content">
        <h3>確認刪除</h3>
        <p>
          {{
            deleteTarget === "comment"
              ? "確定要刪除這則評論嗎？此操作無法復原。"
              : "確定要刪除這則回覆嗎？此操作無法復原。"
          }}
        </p>
        <div class="delete-modal-actions">
          <button @click="showDeleteModal = false" class="cancel-btn">
            取消
          </button>
          <button @click="executeDelete" class="confirm-delete-btn">
            確認刪除
          </button>
        </div>
      </div>
    </div>

    <!-- 舉報模態框 -->
    <div class="report-modal" v-if="showReportModal">
      <div class="report-modal-content">
        <h3>舉報{{ reportTarget === "comment" ? "評論" : "回覆" }}</h3>
        <p>請選擇舉報原因：</p>

        <div class="report-reasons">
          <div
            class="report-reason-item"
            v-for="(reason, index) in reportReasons"
            :key="index"
          >
            <input
              type="checkbox"
              :id="`reason-${index}`"
              v-model="selectedReasons"
              :value="reason"
            />
            <label :for="`reason-${index}`">{{ reason }}</label>
          </div>
        </div>

        <div class="report-description">
          <label for="report-description">詳細描述（選填）：</label>
          <textarea
            id="report-description"
            v-model="reportDescription"
            placeholder="請描述為什麼您認為這條內容需要舉報..."
            rows="3"
          ></textarea>
        </div>

        <div class="report-modal-actions">
          <button @click="cancelReport" class="cancel-btn">取消</button>
          <button
            @click="submitReport"
            class="submit-report-btn"
            :disabled="selectedReasons.length === 0"
          >
            提交舉報
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted } from "vue";
  import { useStore } from "vuex";
  import { useRouter } from "vue-router";
  import MessageService from "@/services/MessageService";

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
      const router = useRouter();

      // 評論相關
      const commentText = ref("");
      const newRating = ref(0);
      const isLoading = ref(true);
      const isSubmitting = ref(false);
      const isLiking = ref(false);

      // 回覆相關
      const replyText = ref("");
      const replyingToId = ref(null);
      const showingRepliesForId = ref(null);
      const isSubmittingReply = ref(false);
      const isLoadingReplies = ref(false);
      const isReplyLiking = ref(false);

      const isLoggedIn = computed(() => store.getters["user/isLoggedIn"]);
      const currentUser = computed(() => store.getters["user/currentUser"]);

      // 刪除評論
      const showDeleteModal = ref(false);
      const deleteTarget = ref(""); // 'comment' 或 'reply'
      const itemToDeleteId = ref(null);

      // 舉報相關
      const showReportModal = ref(false);
      const reportTarget = ref(""); // 'comment' 或 'reply'
      const reportItemId = ref(null);
      const reportDescription = ref("");
      const selectedReasons = ref([]);
      const reportReasons = [
        "垃圾內容/廣告",
        "騷擾或霸凌",
        "冒充他人",
        "不當或冒犯性內容",
        "虛假信息",
        "違反平台規則",
        "其他",
      ];

      // 編輯評論
      const editingCommentId = ref(null);
      const editCommentText = ref("");
      const editRating = ref(0);
      const isSubmittingEdit = ref(false);

      // 編輯回覆
      const editingReplyId = ref(null);
      const editReplyText = ref("");
      const isSubmittingReplyEdit = ref(false);

      // 從 Vuex 獲取評論數據
      const comments = computed(() => {
        return store.getters["commentsModule/getComments"](props.propertyId);
      });

      // 獲取回覆
      const replies = computed(() => {
        return store.getters["commentsModule/allReplies"];
      });

      // 計算平均評分
      const averageRating = computed(() => {
        return store.getters["commentsModule/getPropertyRating"](
          props.propertyId
        );
      });

      // 計算評論數量
      const commentCount = computed(() => {
        return store.getters["commentsModule/commentCount"](props.propertyId);
      });

      // 檢查評論是否已點贊
      const isCommentLiked = (comment) => {
        if (!currentUser.value || !comment.likedBy) return false;
        return comment.likedBy.includes(currentUser.value.user_id);
      };

      // 檢查回覆是否已點贊
      const isReplyLiked = (reply) => {
        if (!currentUser.value || !reply.likes) return false;
        return reply.likes.includes(currentUser.value.user_id);
      };

      // 檢查用戶是否可以編輯評論
      const canEditComment = (comment) => {
        if (!currentUser.value) return false;
        return comment.user_id === currentUser.value.user_id;
      };

      // 檢查用戶是否可以編輯回覆
      const canEditReply = (reply) => {
        if (!currentUser.value) return false;
        return reply.user_id === currentUser.value.user_id;
      };

      // 開始編輯評論
      const startEditComment = (comment) => {
        editingCommentId.value = comment.id;
        editCommentText.value = comment.content;
        editRating.value = comment.rating;
      };

      // 取消編輯評論
      const cancelEditComment = () => {
        editingCommentId.value = null;
        editCommentText.value = "";
        editRating.value = 0;
      };

      // 設置編輯評分
      const setEditRating = (rating) => {
        editRating.value = rating;
      };

      // 更新評論
      const updateComment = async (commentId) => {
        if (!editCommentText.value.trim() || !editRating.value) return;

        isSubmittingEdit.value = true;
        try {
          const result = await store.dispatch("commentsModule/updateComment", {
            commentId,
            content: editCommentText.value.trim(),
            rating: editRating.value,
          });

          if (result) {
            MessageService.success("評論更新成功");

            // 手動更新本地評論數據，確保頁面立即更新
            const commentIndex = comments.value.findIndex(
              (c) => c.id === commentId
            );
            if (commentIndex !== -1) {
              comments.value[commentIndex].content =
                editCommentText.value.trim();
              comments.value[commentIndex].rating = editRating.value;
            }

            // 清空編輯狀態
            editingCommentId.value = null;
            editCommentText.value = "";
            editRating.value = 0;
          } else {
            MessageService.error("評論更新失敗，請稍後再試");
          }
        } catch (error) {
          console.error("更新評論失敗:", error);
          MessageService.error(
            "評論更新失敗: " + (error.message || "未知錯誤")
          );
        } finally {
          isSubmittingEdit.value = false;
        }
      };

      // 打開舉報模態框
      const openReportModal = (target, itemId) => {
        // 如果用戶未登入，跳轉到登入頁面
        if (!isLoggedIn.value) {
          redirectToLogin();
          return;
        }

        // 判斷是否舉報自己的內容
        if (target === "comment") {
          // 找到對應評論
          const comment = comments.value.find((c) => c.id === itemId);

          // 檢查是否為自己的評論
          if (comment && comment.user_id === currentUser.value.user_id) {
            MessageService.warning("您不能舉報自己的評論");
            return;
          }
        } else if (target === "reply") {
          // 找到對應回覆
          const reply = replies.value.find((r) => r.id === itemId);

          // 檢查是否為自己的回覆
          if (reply && reply.user_id === currentUser.value.user_id) {
            MessageService.warning("您不能舉報自己的回覆");
            return;
          }
        }

        // 繼續原有邏輯
        reportTarget.value = target;
        reportItemId.value = itemId;
        selectedReasons.value = [];
        reportDescription.value = "";
        showReportModal.value = true;
      };

      // 取消舉報
      const cancelReport = () => {
        showReportModal.value = false;
      };

      // 提交舉報
      const submitReport = async () => {
        if (selectedReasons.value.length === 0) return;

        try {
          const result = await store.dispatch("commentsModule/reportContent", {
            contentType: reportTarget.value,
            contentId: reportItemId.value,
            reasons: selectedReasons.value,
            description: reportDescription.value.trim(),
          });

          // 關閉模態框
          showReportModal.value = false;

          // 顯示成功提示
          if (result) {
            MessageService.success("舉報已提交，感謝您幫助我們維護社區環境");
          } else {
            MessageService.error("舉報提交失敗，請稍後再試");
          }
        } catch (error) {
          console.error("提交舉報失敗:", error);
          MessageService.error(
            "舉報提交失敗: " + (error.message || "未知錯誤")
          );
        }
      };

      // 在組件掛載時從資料庫加載評論
      onMounted(async () => {
        isLoading.value = true;
        try {
          await store.dispatch("commentsModule/fetchComments", {
            propertyId: props.propertyId,
            page: 1,
            perPage: 50,
          });
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
        if (!commentText.value.trim() || !newRating.value || !isLoggedIn.value)
          return;

        isSubmitting.value = true;
        try {
          const result = await store.dispatch("commentsModule/addComment", {
            propertyId: props.propertyId,
            content: commentText.value.trim(),
            rating: newRating.value,
          });

          if (result) {
            MessageService.success("評論發布成功");
            // 清空表單
            commentText.value = "";
            newRating.value = 0;
          } else {
            MessageService.error("評論發佈失敗，請稍後再試");
          }
        } catch (error) {
          console.error("提交評論失敗:", error);
          MessageService.error(
            "評論發佈失敗: " + (error.message || "未知錯誤")
          );
        } finally {
          isSubmitting.value = false;
        }
      };

      // 點贊評論
      const likeComment = async (commentId) => {
        if (isLiking.value || !isLoggedIn.value) return;

        if (!isLoggedIn.value) {
          redirectToLogin();
          return;
        }

        isLiking.value = true;
        try {
          await store.dispatch("commentsModule/likeComment", commentId);
        } catch (error) {
          console.error("點贊失敗:", error);
        } finally {
          isLiking.value = false;
        }
      };

      // 顯示回覆表單
      const showReplyForm = (commentId) => {
        if (!isLoggedIn.value) {
          redirectToLogin();
          return;
        }

        replyingToId.value = commentId;
        replyText.value = "";
      };

      // 取消回覆
      const cancelReply = () => {
        replyingToId.value = null;
        replyText.value = "";
      };

      // 提交回覆
      const submitReply = async (commentId) => {
        if (!replyText.value.trim() || !isLoggedIn.value) return;

        isSubmittingReply.value = true;
        try {
          const result = await store.dispatch("commentsModule/addReply", {
            commentId,
            content: replyText.value.trim(),
          });

          if (result) {
            MessageService.success("回覆發送成功");

            // 如果用戶正在查看回覆，則重新加載回覆
            if (showingRepliesForId.value === commentId) {
              await showReplies(commentId);
            }

            // 清空表單並隱藏回覆框
            replyText.value = "";
            replyingToId.value = null;
          } else {
            MessageService.error("提交回覆失敗，請稍後再試");
          }
        } catch (error) {
          console.error("提交回覆失敗:", error);
          MessageService.error(
            "提交回覆失敗: " + (error.message || "未知錯誤")
          );
        } finally {
          isSubmittingReply.value = false;
        }
      };

      // 顯示回覆
      const showReplies = async (commentId) => {
        showingRepliesForId.value = commentId;
        isLoadingReplies.value = true;

        try {
          await store.dispatch("commentsModule/fetchReplies", {
            commentId,
            page: 1,
            perPage: 50,
          });
        } catch (error) {
          console.error("獲取回覆失敗:", error);
        } finally {
          isLoadingReplies.value = false;
        }
      };

      // 隱藏回覆
      const hideReplies = () => {
        showingRepliesForId.value = null;
      };

      // 點贊回覆
      const likeReply = async (replyId) => {
        if (isReplyLiking.value || !isLoggedIn.value) return;

        if (!isLoggedIn.value) {
          redirectToLogin();
          return;
        }

        isReplyLiking.value = true;
        try {
          await store.dispatch("commentsModule/likeReply", replyId);
        } catch (error) {
          console.error("點贊回覆失敗:", error);
        } finally {
          isReplyLiking.value = false;
        }
      };

      // 重定向到登入頁面
      const redirectToLogin = () => {
        router.push({
          path: "/login",
          query: { redirect: router.currentRoute.value.fullPath },
        });
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

      // 檢查用戶是否可以刪除評論
      const canDeleteComment = (comment) => {
        if (!currentUser.value) return false;
        return comment.user_id === currentUser.value.user_id;
      };

      // 檢查用戶是否可以刪除回覆
      const canDeleteReply = (reply) => {
        if (!currentUser.value) return false;
        return reply.user_id === currentUser.value.user_id;
      };

      // 確認刪除評論
      const confirmDeleteComment = (commentId) => {
        deleteTarget.value = "comment";
        itemToDeleteId.value = commentId;
        showDeleteModal.value = true;
      };

      // 確認刪除回覆
      const confirmDeleteReply = (replyId) => {
        deleteTarget.value = "reply";
        itemToDeleteId.value = replyId;
        showDeleteModal.value = true;
      };

      // 執行刪除操作
      const executeDelete = async () => {
        try {
          let result = false;

          if (deleteTarget.value === "comment") {
            result = await store.dispatch("commentsModule/deleteComment", {
              propertyId: props.propertyId,
              commentId: itemToDeleteId.value,
            });
          } else if (deleteTarget.value === "reply") {
            result = await store.dispatch(
              "commentsModule/deleteReply",
              itemToDeleteId.value
            );

            // 如果正在顯示回覆，重新載入回覆列表
            if (showingRepliesForId.value) {
              await showReplies(showingRepliesForId.value);
            }
          }

          // 關閉確認對話框
          showDeleteModal.value = false;

          if (result) {
            MessageService.success(
              deleteTarget.value === "comment" ? "評論已刪除" : "回覆已刪除"
            );
          } else {
            MessageService.error("刪除失敗，請稍後再試");
          }
        } catch (error) {
          console.error("刪除失敗:", error);
          MessageService.error("刪除失敗: " + (error.message || "未知錯誤"));
        }
      };

      // 編輯回覆
      const startEditReply = (reply) => {
        editingReplyId.value = reply.id;
        editReplyText.value = reply.content;
      };

      const cancelEditReply = () => {
        editingReplyId.value = null;
        editReplyText.value = "";
      };

      const updateReply = async (replyId) => {
        if (!editReplyText.value.trim()) return;

        isSubmittingReply.value = true;
        try {
          const result = await store.dispatch("commentsModule/updateReply", {
            replyId,
            content: editReplyText.value.trim(),
          });

          if (result) {
            MessageService.success("回覆更新成功");

            // 手動更新本地回覆數據，確保頁面立即更新
            const replyIndex = replies.value.findIndex((r) => r.id === replyId);
            if (replyIndex !== -1) {
              replies.value[replyIndex].content = editReplyText.value.trim();
            }

            // 清除編輯狀態
            cancelEditReply();
          } else {
            MessageService.error("更新回覆失敗，請稍後再試");
          }
        } catch (error) {
          console.error("更新回覆失敗:", error);
          MessageService.error(
            "更新回覆失敗: " + (error.message || "未知錯誤")
          );
        } finally {
          isSubmittingReply.value = false;
        }
      };

      return {
        commentText,
        newRating,
        comments,
        replies,
        averageRating,
        commentCount,
        isLoading,
        isSubmitting,
        isLiking,
        isLoggedIn,
        setRating,
        submitComment,
        likeComment,
        formatDate,
        isCommentLiked,

        // 回覆相關
        replyText,
        replyingToId,
        showingRepliesForId,
        isSubmittingReply,
        isLoadingReplies,
        isReplyLiking,
        showReplyForm,
        cancelReply,
        submitReply,
        showReplies,
        hideReplies,
        likeReply,
        isReplyLiked,
        redirectToLogin,

        // 刪除相關
        showDeleteModal,
        deleteTarget,
        canDeleteComment,
        canDeleteReply,
        confirmDeleteComment,
        confirmDeleteReply,
        executeDelete,

        // 編輯評論相關
        editingCommentId,
        editCommentText,
        editRating,
        isSubmittingEdit,
        canEditComment,
        startEditComment,
        cancelEditComment,
        setEditRating,
        updateComment,

        // 編輯回覆相關
        editingReplyId,
        editReplyText,
        isSubmittingReplyEdit,
        canEditReply,
        startEditReply,
        cancelEditReply,
        updateReply,

        // 舉報相關
        showReportModal,
        reportTarget,
        reportItemId,
        reportDescription,
        selectedReasons,
        reportReasons,
        openReportModal,
        cancelReport,
        submitReport,
      };
    },
  };
</script>

<style scoped>
  /* 整體容器優化 */
  .comments-section {
    margin-top: 30px;
    padding: 0 25px 25px;
    background: linear-gradient(to bottom, #ffffff, #f9fafb);
    border-radius: 12px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.03);
  }

  /* 標題美化 */
  .comments-section h3 {
    font-size: 1.5rem;
    color: #2c3e50;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f2f5;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  /* 評分統計美化 */
  .comment-stats {
    display: inline-flex;
    align-items: center;
    background: #fff;
    padding: 4px 12px;
    border-radius: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  .avg-rating {
    color: #ff9800;
    font-weight: 700;
    font-size: 1.1rem;
    margin-right: 4px;
  }

  .total-comments {
    margin-left: 6px;
    color: #718096;
  }

  .comment-item {
    background: #ffffff;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 18px;
    transition: all 0.3s ease;
    border: 1px solid #f0f2f5;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
  }

  .comment-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
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
    width: 45px;
    height: 45px;
    background: linear-gradient(45deg, #4a6cf7, #3b82f6);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    font-weight: 600;
    box-shadow: 0 3px 10px rgba(59, 130, 246, 0.3);
  }

  .user-avatar.small {
    width: 32px;
    height: 32px;
    font-size: 0.9rem;
  }

  .user-info {
    display: flex;
    flex-direction: column;
  }

  .user-name {
    font-weight: 600;
    color: #2d3748;
    font-size: 1rem;
  }

  .comment-date,
  .reply-date {
    font-size: 0.8rem;
    color: #999;
  }

  .comment-rating {
    color: #ffb700;
    font-size: 1.2rem;
    letter-spacing: 2px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .comment-content {
    color: #333;
    line-height: 1.5;
    margin: 10px 0;
  }

  .comment-actions-top {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .comment-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }

  /* 按鈕基本樣式 */
  button {
    transition: all 0.2s ease;
    font-weight: 500;
    outline: none !important;
  }

  .like-btn,
  .reply-btn {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 6px 12px;
    border-radius: 30px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.9rem;
    color: #64748b;
    transition: all 0.2s;
  }

  .like-btn:hover:not(:disabled),
  .reply-btn:hover {
    background: #edf2f7;
    color: #3b82f6;
    border-color: #cbd5e1;
    transform: translateY(-1px);
  }

  .like-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .like-btn.liked {
    color: #e53e3e;
    border-color: #fed7d7;
    background: #fff5f5;
  }

  .like-icon {
    font-size: 1rem;
  }

  .delete-btn {
    background: transparent;
    border: none;
    font-size: 0.85rem;
    color: #a0aec0;
    padding: 4px 8px;
    border-radius: 4px;
    opacity: 0.7;
    transition: all 0.2s;
  }

  .delete-btn:hover {
    background: #fee2e2;
    color: #e53e3e;
    opacity: 1;
  }

  .delete-btn.small {
    font-size: 0.8rem;
  }

  .material-icons {
    font-size: 18px;
  }

  .delete-btn.small .material-icons {
    font-size: 16px;
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
    gap: 6px;
    color: #e2e8f0;
    font-size: 1.4rem;
    cursor: pointer;
  }

  .star-rating span {
    transition: all 0.2s;
    transform-origin: center;
  }

  .star-rating span:hover {
    color: #fbbf24;
    transform: scale(1.2);
  }

  .star-rating span.active {
    color: #f59e0b;
  }

  textarea {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 12px;
    resize: vertical;
    font-family: inherit;
    font-size: 0.95rem;
    color: #4a5568;
    background: #f8fafc;
    transition: all 0.2s;
    min-height: 80px;
  }

  textarea:focus {
    border-color: #90cdf4;
    background: #fff;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    outline: none;
  }

  .submit-comment {
    background: linear-gradient(to right, #3b82f6, #60a5fa);
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
  }

  .submit-comment:hover:not(:disabled) {
    background: linear-gradient(to right, #2563eb, #3b82f6);
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(59, 130, 246, 0.3);
  }

  .submit-comment:disabled {
    background: #ccc;
    cursor: not-allowed;
    box-shadow: none;
  }

  .login-prompt {
    text-align: center;
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
  }

  .login-btn {
    background: #007bff;
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    margin-top: 10px;
  }

  .login-btn:hover {
    background: #0069d9;
  }

  .no-comments {
    text-align: center;
    color: #718096;
    padding: 35px 20px;
    font-style: italic;
    background: #f8fafc;
    border-radius: 12px;
    border: 1px dashed #cbd5e1;
    margin-top: 20px;
  }

  .no-comments::before {
    content: "💬";
    display: block;
    font-size: 2rem;
    margin-bottom: 10px;
  }

  .loading-comments,
  .loading-replies {
    display: flex;
    justify-content: center;
    padding: 30px 0;
  }

  .loading-spinner {
    display: flex;
    align-items: center;
    color: #718096;
    font-weight: 500;
    letter-spacing: 0.5px;
  }

  .loading-spinner:after {
    content: "";
    width: 20px;
    height: 20px;
    margin-left: 12px;
    border: 3px solid #90cdf4;
    border-radius: 50%;
    border-top-color: #3b82f6;
    animation: spin 0.8s linear infinite;
  }

  /* 回覆相關樣式 */
  .reply-form {
    margin-top: 12px;
    padding: 15px;
    background: #f1f5f9;
    border-radius: 10px;
    border-left: 3px solid #60a5fa;
  }

  .reply-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
  }

  .cancel-reply-btn {
    background: #f0f0f0;
    color: #666;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
  }

  .submit-reply-btn {
    background: #0d6efd;
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
  }

  .submit-reply-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  .show-replies-btn,
  .hide-replies-btn {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    color: #4a6cf7;
    padding: 6px 12px;
    border-radius: 6px;
    margin-top: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
  }

  .show-replies-btn:hover,
  .hide-replies-btn:hover {
    background: #edf2f7;
    color: #3b82f6;
  }

  .replies-list {
    margin-top: 15px;
    padding: 15px;
    background: #f8fafc;
    border-radius: 10px;
    position: relative;
  }

  .replies-container {
    margin-bottom: 10px;
  }

  .reply-item {
    padding: 12px;
    border-bottom: 1px solid #edf2f7;
    transition: background 0.2s;
  }

  .reply-item:hover {
    background: rgba(237, 242, 247, 0.7);
  }

  .reply-item:last-child {
    border-bottom: none;
  }

  .reply-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 5px;
  }

  .reply-user {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .reply-content {
    margin-left: 40px;
    color: #4a5568;
    line-height: 1.5;
  }

  .reply-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 5px;
  }

  .like-btn.small {
    padding: 3px 8px;
    font-size: 0.8rem;
  }

  .no-replies {
    color: #999;
    font-style: italic;
    padding: 5px 0;
    text-align: center;
  }

  .loading-replies {
    display: flex;
    justify-content: center;
    padding: 10px 0;
  }

  .delete-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(3px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .delete-modal-content {
    background: white;
    border-radius: 12px;
    padding: 25px;
    width: 90%;
    max-width: 450px;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    animation: slideUp 0.3s ease;
    transform: translateY(0);
  }

  @keyframes slideUp {
    from {
      transform: translateY(30px);
      opacity: 0.8;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .delete-modal-content h3 {
    margin-top: 0;
    color: #e53e3e;
    font-size: 1.5rem;
    border-bottom: none;
  }

  .delete-modal-content p {
    color: #4a5568;
    line-height: 1.6;
    margin-bottom: 20px;
  }

  .delete-modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 25px;
  }

  .cancel-btn {
    background: #f7fafc;
    color: #4a5568;
    border: 1px solid #e2e8f0;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
  }

  .cancel-btn:hover {
    background: #edf2f7;
  }

  .confirm-delete-btn {
    background: #e53e3e;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    box-shadow: 0 4px 10px rgba(229, 62, 62, 0.2);
  }

  .confirm-delete-btn:hover {
    background: #c53030;
    box-shadow: 0 6px 15px rgba(229, 62, 62, 0.3);
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }

  /* 編輯評論/回覆相關樣式 */
  .edit-comment-form,
  .edit-reply-form {
    margin: 10px 0;
    padding: 15px;
    background: #f8fafc;
    border-radius: 10px;
    border-left: 3px solid #3b82f6;
    animation: expandForm 0.3s ease-out;
  }

  .edit-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 10px;
  }

  .cancel-edit-btn {
    background: #f0f0f0;
    color: #666;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .cancel-edit-btn:hover {
    background: #e2e2e2;
  }

  .update-comment-btn,
  .update-reply-btn {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 6px rgba(59, 130, 246, 0.1);
  }

  .update-comment-btn:hover,
  .update-reply-btn:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 6px 8px rgba(59, 130, 246, 0.2);
  }

  .update-comment-btn:disabled,
  .update-reply-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  /* 評論和回覆選項按鈕 */
  .comment-options,
  .reply-options {
    display: flex;
    gap: 8px;
    margin-left: 10px;
  }

  .edit-btn,
  .report-btn {
    background: transparent;
    border: none;
    color: #a0aec0;
    padding: 4px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    opacity: 0.7;
  }

  .edit-btn:hover {
    background: #edf2f7;
    color: #3b82f6;
    opacity: 1;
  }

  .report-btn:hover {
    background: #fff5f5;
    color: #e53e3e;
    opacity: 1;
  }

  .edit-btn.small,
  .report-btn.small {
    font-size: 0.8rem;
  }

  /* 舉報模態框樣式 */
  .report-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(3px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;
  }

  .report-modal-content {
    background: white;
    border-radius: 12px;
    padding: 25px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
    animation: slideUp 0.3s ease;
    max-height: 90vh;
    overflow-y: auto;
  }

  .report-modal-content h3 {
    margin-top: 0;
    color: #2d3748;
    font-size: 1.5rem;
    border-bottom: none;
    margin-bottom: 20px;
  }

  .report-reasons {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }

  .report-reason-item {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .report-reason-item input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }

  .report-reason-item label {
    font-size: 1rem;
    color: #4a5568;
    cursor: pointer;
  }

  .report-description {
    margin-bottom: 20px;
  }

  .report-description label {
    display: block;
    margin-bottom: 8px;
    font-size: 1rem;
    color: #4a5568;
  }

  .submit-report-btn {
    background: #e53e3e;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    box-shadow: 0 4px 10px rgba(229, 62, 62, 0.2);
  }

  .submit-report-btn:hover:not(:disabled) {
    background: #c53030;
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(229, 62, 62, 0.3);
  }

  .submit-report-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
</style>
