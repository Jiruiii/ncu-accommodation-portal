import apiService from '@/services/api';

export default {
  namespaced: true,
  
  state: {
    topics: [],
    currentTopic: null,
    posts: [],
    currentPost: null,
    replies: [],
    loading: false,
    error: null,
    pagination: {
      total: 0,
      currentPage: 1,
      totalPages: 1,
    }
  },
  
  mutations: {
    SET_LOADING(state, status) {
      state.loading = status;
    },
    
    SET_ERROR(state, error) {
      state.error = error;
    },
    
    SET_TOPICS(state, { topics, total, pages, currentPage }) {
      state.topics = topics;
      state.pagination.total = total;
      state.pagination.totalPages = pages;
      state.pagination.currentPage = currentPage;
    },
    
    SET_CURRENT_TOPIC(state, topic) {
      state.currentTopic = topic;
    },
    
    SET_POSTS(state, { posts, total, pages, currentPage }) {
      state.posts = posts;
      state.pagination.total = total;
      state.pagination.totalPages = pages;
      state.pagination.currentPage = currentPage;
    },
    
    SET_CURRENT_POST(state, post) {
      state.currentPost = post;
    },
    
    SET_REPLIES(state, { replies, total, pages, currentPage }) {
      state.replies = replies;
      state.pagination.total = total;
      state.pagination.totalPages = pages;
      state.pagination.currentPage = currentPage;
    },
    
    UPDATE_POST_LIKES(state, { postId, likes, likeCount }) {
      const postIndex = state.posts.findIndex(post => post.id === postId);
      if (postIndex !== -1) {
        state.posts[postIndex].likes = likes;
        state.posts[postIndex].like_count = likeCount;
      }
      
      if (state.currentPost && state.currentPost.id === postId) {
        state.currentPost.likes = likes;
        state.currentPost.like_count = likeCount;
      }
    },
    
    UPDATE_REPLY_LIKES(state, { replyId, likes, likeCount }) {
      const replyIndex = state.replies.findIndex(reply => reply.id === replyId);
      if (replyIndex !== -1) {
        state.replies[replyIndex].likes = likes;
        state.replies[replyIndex].like_count = likeCount;
      }
    },
    
    ADD_TOPIC(state, topic) {
      state.topics.unshift(topic);
    },
    
    ADD_POST(state, post) {
      state.posts.push(post);
    },
    
    ADD_REPLY(state, reply) {
      state.replies.push(reply);
    },
    
    UPDATE_TOPIC(state, updatedTopic) {
      const index = state.topics.findIndex(topic => topic.id === updatedTopic.id);
      if (index !== -1) {
        state.topics.splice(index, 1, updatedTopic);
      }
      
      if (state.currentTopic && state.currentTopic.id === updatedTopic.id) {
        state.currentTopic = updatedTopic;
      }
    },
    
    UPDATE_POST(state, updatedPost) {
      const index = state.posts.findIndex(post => post.id === updatedPost.id);
      if (index !== -1) {
        state.posts.splice(index, 1, updatedPost);
      }
      
      if (state.currentPost && state.currentPost.id === updatedPost.id) {
        state.currentPost = updatedPost;
      }
    },
    
    UPDATE_REPLY(state, updatedReply) {
      const index = state.replies.findIndex(reply => reply.id === updatedReply.id);
      if (index !== -1) {
        state.replies.splice(index, 1, updatedReply);
      }
    },
    
    REMOVE_TOPIC(state, topicId) {
      state.topics = state.topics.filter(topic => topic.id !== topicId);
    },
    
    REMOVE_POST(state, postId) {
      state.posts = state.posts.filter(post => post.id !== postId);
    },
    
    REMOVE_REPLY(state, replyId) {
      state.replies = state.replies.filter(reply => reply.id !== replyId);
    }
  },
  
  actions: {
    // 主題相關操作
    async fetchTopics({ commit }, { page = 1, perPage = 10 } = {}) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.getTopics(page, perPage);
        commit('SET_TOPICS', {
          topics: response.topics,
          total: response.total,
          pages: response.pages,
          currentPage: response.current_page
        });
        return response.topics;
      } catch (error) {
        commit('SET_ERROR', error.message || '獲取主題列表失敗');
        console.error('獲取主題列表失敗', error);
        return [];
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async fetchTopic({ commit }, topicId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.getTopic(topicId);
        commit('SET_CURRENT_TOPIC', response);
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '獲取主題詳情失敗');
        console.error('獲取主題詳情失敗', error);
        return null;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async createTopic({ commit }, data) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.createTopic(data);
        commit('ADD_TOPIC', response);
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '創建主題失敗');
        console.error('創建主題失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async updateTopic({ commit }, { topicId, data }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.updateTopic(topicId, data);
        commit('UPDATE_TOPIC', response);
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '更新主題失敗');
        console.error('更新主題失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async deleteTopic({ commit }, topicId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        await apiService.discussion.deleteTopic(topicId);
        commit('REMOVE_TOPIC', topicId);
        return true;
      } catch (error) {
        commit('SET_ERROR', error.message || '刪除主題失敗');
        console.error('刪除主題失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 文章相關操作
    async fetchPosts({ commit }, { topicId, page = 1, perPage = 20 }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.getPosts(topicId, page, perPage);
        
        if (response.topic) {
          commit('SET_CURRENT_TOPIC', response.topic);
        }
        
        commit('SET_POSTS', {
          posts: response.posts,
          total: response.total,
          pages: response.pages,
          currentPage: response.current_page
        });
        
        return response.posts;
      } catch (error) {
        commit('SET_ERROR', error.message || '獲取文章列表失敗');
        console.error('獲取文章列表失敗', error);
        return [];
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async createPost({ commit }, { topicId, data }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.createPost(topicId, data);
        commit('ADD_POST', response);
        
        // 如果有當前主題，更新其文章數量
        if (this.state.discussion.currentTopic) {
          const updatedTopic = { 
            ...this.state.discussion.currentTopic,
            post_count: (this.state.discussion.currentTopic.post_count || 0) + 1 
          };
          commit('SET_CURRENT_TOPIC', updatedTopic);
        }
        
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '發表文章失敗');
        console.error('發表文章失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async updatePost({ commit }, { postId, data }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.updatePost(postId, data);
        commit('UPDATE_POST', response);
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '更新文章失敗');
        console.error('更新文章失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async deletePost({ commit, state }, postId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        await apiService.discussion.deletePost(postId);
        commit('REMOVE_POST', postId);
        
        // 如果有當前主題，更新其文章數量
        if (state.currentTopic) {
          const updatedTopic = { 
            ...state.currentTopic,
            post_count: Math.max(0, (state.currentTopic.post_count || 0) - 1)
          };
          commit('SET_CURRENT_TOPIC', updatedTopic);
        }
        
        return true;
      } catch (error) {
        commit('SET_ERROR', error.message || '刪除文章失敗');
        console.error('刪除文章失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 回覆相關操作
    async fetchReplies({ commit }, { postId, page = 1, perPage = 50 }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.getReplies(postId, page, perPage);
        
        if (response.post) {
          commit('SET_CURRENT_POST', response.post);
        }
        
        commit('SET_REPLIES', {
          replies: response.replies,
          total: response.total,
          pages: response.pages,
          currentPage: response.current_page
        });
        
        return response.replies;
      } catch (error) {
        commit('SET_ERROR', error.message || '獲取回覆列表失敗');
        console.error('獲取回覆列表失敗', error);
        return [];
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async createReply({ commit }, { postId, data }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.createReply(postId, data);
        commit('ADD_REPLY', response);
        
        // 如果有當前文章，更新其回覆數量
        if (this.state.discussion.currentPost) {
          const updatedPost = { 
            ...this.state.discussion.currentPost,
            reply_count: (this.state.discussion.currentPost.reply_count || 0) + 1 
          };
          commit('SET_CURRENT_POST', updatedPost);
        }
        
        // 更新文章列表中的回覆數量
        const postsIndex = this.state.discussion.posts.findIndex(post => post.id === postId);
        if (postsIndex !== -1) {
          const updatedPosts = [...this.state.discussion.posts];
          updatedPosts[postsIndex] = {
            ...updatedPosts[postsIndex],
            reply_count: (updatedPosts[postsIndex].reply_count || 0) + 1
          };
          commit('SET_POSTS', {
            posts: updatedPosts,
            total: this.state.discussion.pagination.total,
            pages: this.state.discussion.pagination.totalPages,
            currentPage: this.state.discussion.pagination.currentPage
          });
        }
        
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '發表回覆失敗');
        console.error('發表回覆失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async updateReply({ commit }, { replyId, data }) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        const response = await apiService.discussion.updateReply(replyId, data);
        commit('UPDATE_REPLY', response);
        return response;
      } catch (error) {
        commit('SET_ERROR', error.message || '更新回覆失敗');
        console.error('更新回覆失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    async deleteReply({ commit, state }, replyId) {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      try {
        await apiService.discussion.deleteReply(replyId);
        
        // 找到被刪除回覆的文章ID
        const reply = state.replies.find(r => r.id === replyId);
        const postId = reply?.post_id;
        
        commit('REMOVE_REPLY', replyId);
        
        // 如果有當前文章且回覆屬於該文章，更新其回覆數量
        if (state.currentPost && postId === state.currentPost.id) {
          const updatedPost = { 
            ...state.currentPost,
            reply_count: Math.max(0, (state.currentPost.reply_count || 0) - 1)
          };
          commit('SET_CURRENT_POST', updatedPost);
        }
        
        // 更新文章列表中的回覆數量
        if (postId) {
          const postsIndex = state.posts.findIndex(post => post.id === postId);
          if (postsIndex !== -1) {
            const updatedPosts = [...state.posts];
            updatedPosts[postsIndex] = {
              ...updatedPosts[postsIndex],
              reply_count: Math.max(0, (updatedPosts[postsIndex].reply_count || 0) - 1)
            };
            commit('SET_POSTS', {
              posts: updatedPosts,
              total: state.pagination.total,
              pages: state.pagination.totalPages,
              currentPage: state.pagination.currentPage
            });
          }
        }
        
        return true;
      } catch (error) {
        commit('SET_ERROR', error.message || '刪除回覆失敗');
        console.error('刪除回覆失敗', error);
        throw error;
      } finally {
        commit('SET_LOADING', false);
      }
    },
    
    // 讚相關操作
    async likePost({ commit }, postId) {
      try {
        const response = await apiService.discussion.likePost(postId);
        commit('UPDATE_POST_LIKES', {
          postId,
          likes: response.likes,
          likeCount: response.like_count
        });
        return response;
      } catch (error) {
        console.error('操作文章讚失敗', error);
        throw error;
      }
    },
    
    async likeReply({ commit }, replyId) {
      try {
        const response = await apiService.discussion.likeReply(replyId);
        commit('UPDATE_REPLY_LIKES', {
          replyId,
          likes: response.likes,
          likeCount: response.like_count
        });
        return response;
      } catch (error) {
        console.error('操作回覆讚失敗', error);
        throw error;
      }
    },
    
    // 管理員功能
    async pinTopic({ commit }, topicId) {
      try {
        const response = await apiService.discussion.pinTopic(topicId);
        
        // 更新主題列表中的置頂狀態
        const topics = [...this.state.discussion.topics];
        const index = topics.findIndex(t => t.id === topicId);
        
        if (index !== -1) {
          topics[index] = { ...topics[index], is_pinned: response.is_pinned };
          
          // 如果狀態改變，可能需要重新排序
          if (response.is_pinned) {
            // 移到最前面
            const pinnedTopic = topics.splice(index, 1)[0];
            topics.unshift(pinnedTopic);
          }
          
          commit('SET_TOPICS', {
            topics,
            total: this.state.discussion.pagination.total,
            pages: this.state.discussion.pagination.totalPages,
            currentPage: this.state.discussion.pagination.currentPage
          });
        }
        
        // 如果是當前主題，也要更新
        if (this.state.discussion.currentTopic && this.state.discussion.currentTopic.id === topicId) {
          commit('SET_CURRENT_TOPIC', {
            ...this.state.discussion.currentTopic,
            is_pinned: response.is_pinned
          });
        }
        
        return response;
      } catch (error) {
        console.error('置頂/取消置頂主題失敗', error);
        throw error;
      }
    },
    
    async pinPost({ commit }, postId) {
      try {
        const response = await apiService.discussion.pinPost(postId);
        
        // 更新文章列表中的置頂狀態
        const posts = [...this.state.discussion.posts];
        const index = posts.findIndex(p => p.id === postId);
        
        if (index !== -1) {
          posts[index] = { ...posts[index], is_pinned: response.is_pinned };
          
          // 如果狀態改變，可能需要重新排序
          if (response.is_pinned) {
            // 移到最前面
            const pinnedPost = posts.splice(index, 1)[0];
            posts.unshift(pinnedPost);
          }
          
          commit('SET_POSTS', {
            posts,
            total: this.state.discussion.pagination.total,
            pages: this.state.discussion.pagination.totalPages,
            currentPage: this.state.discussion.pagination.currentPage
          });
        }
        
        // 如果是當前文章，也要更新
        if (this.state.discussion.currentPost && this.state.discussion.currentPost.id === postId) {
          commit('SET_CURRENT_POST', {
            ...this.state.discussion.currentPost,
            is_pinned: response.is_pinned
          });
        }
        
        return response;
      } catch (error) {
        console.error('置頂/取消置頂文章失敗', error);
        throw error;
      }
    }
  },
  
  getters: {
    isLoading: state => state.loading,
    error: state => state.error,
    allTopics: state => state.topics,
    getTopic: state => topicId => state.topics.find(t => t.id === topicId),
    currentTopic: state => state.currentTopic,
    allPosts: state => state.posts,
    getPost: state => postId => state.posts.find(p => p.id === postId),
    currentPost: state => state.currentPost,
    allReplies: state => state.replies,
    getReply: state => replyId => state.replies.find(r => r.id === replyId),
    pinnedTopics: state => state.topics.filter(t => t.is_pinned),
    regularTopics: state => state.topics.filter(t => !t.is_pinned),
    pinnedPosts: state => state.posts.filter(p => p.is_pinned),
    regularPosts: state => state.posts.filter(p => !p.is_pinned),
    pagination: state => state.pagination
  }
};