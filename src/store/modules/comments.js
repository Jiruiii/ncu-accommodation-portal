import apiService from '@/services/api';

export default {
  namespaced: true,
  
  state: {
    comments: {},  // { propertyId: [comment1, comment2, ...] }
    currentComment: null,
    replies: [],
    loading: false,
    error: null,
    pagination: {
      total: 0,
      currentPage: 1,
      totalPages: 1,
    }
  },
  
  getters: {
    isLoading: state => state.loading,
    error: state => state.error,
    getComments: state => propertyId => state.comments[propertyId] || [],
    getPropertyRating: state => propertyId => {
      const comments = state.comments[propertyId] || [];
      if (comments.length === 0) return 0;
      
      const sum = comments.reduce((total, comment) => total + comment.rating, 0);
      return (sum / comments.length).toFixed(1);
    },
    commentCount: state => propertyId => (state.comments[propertyId] || []).length,
    allReplies: state => state.replies
  },
  
  mutations: {
    SET_LOADING(state, status) {
      state.loading = status;
    },
    
    SET_ERROR(state, error) {
      state.error = error;
    },
    
    SET_COMMENTS(state, { propertyId, comments }) {
      state.comments = {
        ...state.comments,
        [propertyId]: comments
      };
    },
    
    SET_CURRENT_COMMENT(state, comment) {
      state.currentComment = comment;
    },
    
    SET_REPLIES(state, replies) {
      state.replies = replies;
    },
    
    SET_PAGINATION(state, pagination) {
      state.pagination = pagination;
    },
    
    ADD_COMMENT(state, { propertyId, comment }) {
      if (!state.comments[propertyId]) {
        state.comments[propertyId] = [];
      }
      state.comments[propertyId] = [comment, ...state.comments[propertyId]];
    },
    
    UPDATE_COMMENT(state, { propertyId, commentId, data }) {
      const comments = state.comments[propertyId] || [];
      const index = comments.findIndex(c => c.id === commentId);
      
      if (index !== -1) {
        state.comments[propertyId][index] = {
          ...state.comments[propertyId][index],
          ...data
        };
      }
    },
    
    DELETE_COMMENT(state, { propertyId, commentId }) {
      if (state.comments[propertyId]) {
        state.comments[propertyId] = state.comments[propertyId].filter(
          c => c.id !== commentId
        );
      }
    },
    
    ADD_REPLY(state, reply) {
      state.replies = [...state.replies, reply];
      
      // 更新評論的回覆計數
      const propertyId = state.currentComment?.property_id;
      const commentId = reply.comment_id;
      
      if (propertyId && state.comments[propertyId]) {
        const commentIndex = state.comments[propertyId].findIndex(c => c.id === commentId);
        if (commentIndex !== -1) {
          state.comments[propertyId][commentIndex].replyCount += 1;
        }
      }
    },
    
    UPDATE_REPLY(state, { replyId, data }) {
      const index = state.replies.findIndex(r => r.id === replyId);
      if (index !== -1) {
        state.replies[index] = { ...state.replies[index], ...data };
      }
    },
    
    DELETE_REPLY(state, { replyId, commentId, propertyId }) {
      // 移除回覆
      state.replies = state.replies.filter(r => r.id !== replyId);
      
      // 更新評論的回覆計數
      if (propertyId && commentId && state.comments[propertyId]) {
        const commentIndex = state.comments[propertyId].findIndex(c => c.id === commentId);
        if (commentIndex !== -1 && state.comments[propertyId][commentIndex].replyCount > 0) {
          state.comments[propertyId][commentIndex].replyCount -= 1;
        }
      }
    },
  },
  
  actions: {
    // 獲取特定房源的評論
    async fetchComments({ commit }, { propertyId, page = 1, perPage = 20 }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.comments.getPropertyComments(propertyId, { page, perPage });
        
        commit('SET_COMMENTS', { propertyId, comments: response.comments });
        commit('SET_PAGINATION', {
          total: response.total,
          currentPage: response.current_page,
          totalPages: response.pages
        });
        
        return response.comments;
      } catch (error) {
        commit('SET_ERROR', error.message || '無法獲取評論');
        console.error('獲取評論失敗:', error);
        return [];
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 新增評論
    async addComment({ commit }, { propertyId, content, rating }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.comments.createComment(propertyId, { content, rating });
        commit('ADD_COMMENT', { propertyId, comment: response });
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '無法新增評論');
        console.error('新增評論失敗:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 更新評論
    async updateComment({ commit }, { propertyId, commentId, data }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.comments.updateComment(commentId, data);
        commit('UPDATE_COMMENT', { propertyId, commentId, data: response });
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '無法更新評論');
        console.error('更新評論失敗:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 刪除評論
    async deleteComment({ commit }, { propertyId, commentId }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        await apiService.comments.deleteComment(commentId);
        commit('DELETE_COMMENT', { propertyId, commentId });
        return true;
      } catch (error) {
        commit('SET_ERROR', error.message || '無法刪除評論');
        console.error('刪除評論失敗:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 獲取評論回覆
    async fetchReplies({ commit }, { commentId, page = 1, perPage = 50 }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.comments.getReplies(commentId, { page, perPage });
        
        commit('SET_CURRENT_COMMENT', response.comment);
        commit('SET_REPLIES', response.replies);
        commit('SET_PAGINATION', {
          total: response.total,
          currentPage: response.current_page,
          totalPages: response.pages
        });
        
        return response.replies;
      } catch (error) {
        commit('SET_ERROR', error.message || '無法獲取回覆');
        console.error('獲取回覆失敗:', error);
        return [];
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 新增回覆
    async addReply({ commit, state }, { commentId, content }) {
      try {
        const response = await apiService.comments.createReply(commentId, { content });
        
        // 找出評論所屬的房源 ID
        let propertyId = null;
        for (const [propId, commentsList] of Object.entries(state.comments)) {
          const comment = commentsList.find(c => c.id === commentId);
          if (comment) {
            propertyId = parseInt(propId);
            break;
          }
        }
        
        // 新增回覆到 state
        commit('ADD_REPLY', response);
        
        // 更新評論的回覆計數
        if (propertyId) {
          const commentsList = state.comments[propertyId];
          const commentIndex = commentsList.findIndex(c => c.id === commentId);
          
          if (commentIndex !== -1) {
            const updatedReplyCount = (commentsList[commentIndex].replyCount || 0) + 1;
            
            commit('UPDATE_COMMENT', {
              propertyId,
              commentId,
              data: {
                replyCount: updatedReplyCount
              }
            });
          }
        }
        
        return response;
      } catch (error) {
        console.error('新增回覆失敗:', error);
        throw error;
      }
    },
    
    // 更新回覆
    async updateReply({ commit }, { replyId, content }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.comments.updateReply(replyId, { content });
        commit('UPDATE_REPLY', { replyId, data: response });
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '無法更新回覆');
        console.error('更新回覆失敗:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 刪除回覆
    async deleteReply({ commit, state }, replyId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        // 在刪除前先獲取回覆相關信息
        const replyToDelete = state.replies.find(r => r.id === replyId);
        if (!replyToDelete) {
          throw new Error('找不到要刪除的回覆');
        }
        
        const commentId = replyToDelete.comment_id;
        
        // 找出評論所屬的房源 ID
        let propertyId = null;
        if (state.currentComment && state.currentComment.id === commentId) {
          propertyId = state.currentComment.property_id;
        } else {
          // 查找所有房源的評論
          for (const [propId, commentsList] of Object.entries(state.comments)) {
            const comment = commentsList.find(c => c.id === commentId);
            if (comment) {
              propertyId = parseInt(propId);
              break;
            }
          }
        }
        
        // 調用 API 刪除回覆
        await apiService.comments.deleteReply(replyId);
        
        // 同時更新 state 中的回覆和評論計數
        commit('DELETE_REPLY', { replyId, commentId, propertyId });
        
        return true;
      } catch (error) {
        commit('SET_ERROR', error.message || '無法刪除回覆');
        console.error('刪除回覆失敗:', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 點讚/取消點讚評論
    async likeComment({ commit, state }, commentId) {
      try {
        const response = await apiService.comments.likeComment(commentId);
        
        // 找出評論所屬的房源 ID
        let propertyId = null;
        for (const [propId, commentsList] of Object.entries(state.comments)) {
          const comment = commentsList.find(c => c.id === commentId);
          if (comment) {
            propertyId = parseInt(propId);
            break;
          }
        }
        
        if (propertyId) {
          // 更新評論的讚數和讚列表
          commit('UPDATE_COMMENT', {
            propertyId,
            commentId,
            data: {
              likes: response.likes,
              likedBy: response.likedBy
            }
          });
        }
        
        return response;
      } catch (error) {
        console.error('點讚評論失敗:', error);
        throw error;
      }
    },
    
    // 點讚/取消點讚回覆
    async likeReply({ commit }, replyId) {
      try {
        const response = await apiService.comments.likeReply(replyId);
        
        commit('UPDATE_REPLY', {
          replyId,
          data: {
            like_count: response.like_count,
            likes: response.likes
          }
        });
        
        return response;
      } catch (error) {
        console.error('點讚回覆失敗:', error);
        throw error;
      }
    }
  }
};