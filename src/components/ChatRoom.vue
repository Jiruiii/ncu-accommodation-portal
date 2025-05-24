<template>
    <div class="chatroom-flame">
        <div class="user-choose" v-if="!userselected">   
            <div class="user-selector" v-for="user in userList" @click="chooseUser(user.id)">
                <img class="landlord-image" :src="user.image" />
                <div class="landlord-name">{{user.name}}</div>
            </div>
        </div>
        <div class="chatroom-content" v-else-if="userselected">
            <div class="chatroom-title">
                <div class="chat-person">
                    <i class="fa-solid fa-arrow-left" id="back-btn" @click="chooseUser(targetUserId)"></i>
                    <img class="landlord-image" :src="userList.find(user => user.id === targetUserId)?.image" />
                    <div class="landlord-name">{{userList.find(user => user.id === targetUserId)?.name}}</div>
                </div>
                <i class="fa-solid fa-phone" style="color: black; font-size: 25px; cursor: pointer;"></i>
            </div>
            <div class="chatroom" ref="chatContainer">
                <div v-for="msg in allMessages" :key="msg.time" :class="{ 'my-message': msg.fromTenant, 'other-message': !msg.fromTenant }">
                    <div class="msg-tenant" v-if="msg.fromTenant">
                        <div class="time">{{msg.time}}</div>
                        <div class="message-tenant">{{msg.text}}</div>
                        <img class="msg-tenant-image"  src="https://randomuser.me/api/portraits/women/65.jpg" />
                    </div>
                    <div class="msg-landlord" v-else>
                        <img class="msg-landlord-image" src="https://randomuser.me/api/portraits/men/42.jpg" />
                        <div class="message-landlord">{{msg.text}}</div>
                        <div class="time">{{msg.time}}</div>
                    </div>
                </div>
            </div>
        
            <div class="input-flame">
                <input placeholder="請輸入文字..." v-model.trim="msg" @keydown.enter="addMessages"/>
                <div class="send-button" @click="addMessages"><i class="fa-solid fa-paper-plane"></i></div>
            </div>
        </div>
    </div>
</template>

<script>
    import { ref, onMounted, nextTick, watch } from "vue";
    import { useRouter } from "vue-router";
    import apiService from "@/services/api";
    import { io } from "socket.io-client";

    export default{
        name: "ChatRoom",
        setup (){
            const router = useRouter();
            const msgsTenant = ref([]);
            const msg = ref("");
            const chatContainer = ref(null);
            const jsonData = ref(null);
            const user = ref([]); 
            const userId = ref(8);
            const targetUserId = ref(9);
            const allMessages = ref([]);
            const msg_all = ref("");
            const time_all = ref("");
            const userselected = ref(false);

            const userList = ref([
                { id: 1, name: "張先生", image: "https://randomuser.me/api/portraits/men/42.jpg" },
                { id: 2, name: "張先生", image: require("@/assets/default-avatar.jpg") },
                { id: 3, name: "張先生", image: "https://randomuser.me/api/portraits/men/42.jpg" },
                { id: 9, name: "test1", image: require("@/assets/default-avatar.jpg") },
            ]); 

            // 判斷是否選擇聊天對象
            const chooseUser = (id) => {
                userselected.value = !userselected.value;
                //targetUserId.value = Number(id);
            }

            // 添加訊息
            const addMessages = () => {
                const formattedTime = new Intl.DateTimeFormat("zh-TW", {
                    hour: "numeric",
                    minute: "numeric",
                    hour12: true,
                    timeZone: "Asia/Taipei"
                }).format(new Date()).replace("AM", "上午").replace("PM", "下午");

                allMessages.value.push({
                    fromTenant: true,
                    text: msg.value,
                    time: formattedTime
                });

                sendMessage();

                msg.value = "";  // 清空輸入框

                // 有新訊息自動滾動到底部 
                nextTick(() => {
                    if (chatContainer.value) {
                        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                    }
                });  
            };

            // 建立 WebSocket 連線
            const socket = io("http://localhost:5000", {
                transports: ["websocket"] 
            });

            socket.on("connect", () => {
                console.log("WebSocket 連線成功！");  
                socket.emit("join_room", { user_id: userId.value });
            });

            socket.on("connect_error", (err) => {
                console.error("WebSocket 連線失敗！", err);
            });

            // 監聽訊息
            socket.on("new_message", (data) => {
                // 確保只有來自其他人的訊息才加入 `allMessages`
                if (String(data.sender) !== String(userId.value)) {
                    allMessages.value.push({
                        fromTenant: false, // 因為這是對方傳的
                        text: data.message,
                        time: data.time
                    });

                    // 有新訊息自動滾動到底部
                    nextTick(() => {
                        if (chatContainer.value) {
                            chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                        }
                    });
                }
            });

            // 發送訊息給其他用戶
            const sendMessage = () => {
                const latestMsg = msg.value.trim();
                const latestTime = new Date();

                console.log("送出訊息:", latestMsg);  
                socket.emit("new_message", { 
                    sender: userId.value, 
                    receiver: targetUserId.value, 
                    message: latestMsg, 
                    time: latestTime 
                });
            };

            // 取得用戶的 id
            const fetchData = async () => {
                try {
                    const response = await apiService.users.getProfile();
                    const userData = response.user;

                    user.value = userData;
                    userId.value = userData.user_id;

                    console.log("獲取的 ID:", userId.value);
                    return userData.user_id; 
                } catch (error) {
                    console.error("讀取 JSON 失敗:", error);
                }
            };

            // 取得聊天紀錄
            const fetchHistory = async (senderId, receiverId) => {
                try {
                    const response = await fetch(`http://localhost:5000/api/chat/history?sender_id=${senderId}&receiver_id=${receiverId}`);
                    const history = await response.json();

                    console.log("取得歷史紀錄:", history);
                    
                    allMessages.value = history.map(msg => {
                        const isTenant = String(msg.sender) === String(userId.value) || String(msg.receiver) !== String(userId.value);
                        const formattedTime = new Intl.DateTimeFormat("zh-TW", {
                            hour: "numeric",
                            minute: "numeric",
                            hour12: true,
                            timeZone: "Asia/Taipei"
                        }).format(new Date(msg.timestamp)).replace("AM", "上午").replace("PM", "下午");

                        return {
                            fromTenant: isTenant,
                            text: msg.text,
                            time: formattedTime
                        };
                    });

                } catch (error) {
                    console.error("獲取歷史訊息失敗:", error);
                }
            };

            onMounted(async () => {
                const currentUserId = await fetchData();
                userId.value = currentUserId;
                
                socket.emit("join_room", { user_id: currentUserId });

                // 先移除所有舊的監聽，避免累積事件
                socket.off("new_message"); 

                socket.on("new_message", (data) => {
                    console.log(`收到來自 ${data.sender} 的訊息:`, data.message);

                    allMessages.value.push({
                        fromTenant: false,
                        text: data.message,
                        time: data.time
                    });

                    nextTick(() => {
                        if (chatContainer.value) {
                            chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                        }
                    });

                });

                // 確保 userId 和 targetUserId 都有值再執行 fetchHistory
                if (currentUserId && targetUserId.value) {
                    await fetchHistory(currentUserId, targetUserId.value); // 傳正確 ID
                }

                nextTick(() => {
                    if (chatContainer.value) {
                        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                    }
                });
            }); 

            return { 
                msg,
                addMessages,
                chatContainer,
                jsonData,
                user,
                userId,
                targetUserId,
                fetchHistory,
                allMessages,
                userselected,
                chooseUser,
                userList,
            };
        },
    }
</script>

<style scoped>
    .chatroom-flame{
        
    }
    .user-choose{
        height: 500px;
        padding: 30px;
    }
    .user-selector{
        display: flex;
        align-items: center;
        padding: 10px;
        padding-left: 20px;
        margin: 20px;
        background-color: #F0F0F0;
        border-radius: 12px;
        cursor: pointer;
    }
    .user-selector:hover{
        background-color: #D0D0D0;
    }
    .chatroom-content{
        display: flex;
        flex-direction: column;
        background-color: white;
        padding: 30px; 
        height: 100vh;
    }
    .chatroom-title{
        background-color: #84C1FF;
        padding: 20px;
        border-bottom: 2px solid white;
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .chat-person{
        display: flex;
        align-items: center;
    }
    #back-btn{
        color: black; 
        font-size: 25px; 
        margin-right: 20px;
        cursor: pointer;
    }
    .landlord-image{
        width: 50px;
        height: 50px;
        border-radius: 100%;
        margin-right: 20px;
    }
    .landlord-name{
        font-size: 20px;
        font-weight: bold;
    }
    .chatroom{
        max-height: 430px;
        overflow-y: auto;
        flex-grow: 1;  /* 占滿可用空間 */
        background-color: #C4E1FF;
        padding-top: 20px;
        display: flex;
        flex-direction: column;
    }
    .msg-landlord, .msg-tenant{
        display: flex;
        align-items: center;
    }
    .msg-tenant{
        justify-content: end;
    }
    .msg-landlord-image, .msg-tenant-image{
        width: 30px;
        height: 30px;
        border-radius: 100%;
        margin: 20px;
    }
    .message-landlord, .message-tenant{
        font-size: 16px;
        background-color: #F0F0F0;
        border-radius: 15px;
        padding: 10px;
    }
    .message-tenant{
        background-color: #007bff;
    }
    .time{
        font-size: 10px;
        color: 	#9D9D9D;
        margin: 5px;
    }
    .input-flame{
        height: 220px;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        background-color: #C4E1FF;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
    }
    input{
        position: absolute;
        left: 20px;
        right: 60px;
        bottom: 20px;
        margin-right: 20px;
        padding: 10px;
        border: none;
        border-radius: 15px;
    }
    input:focus{
        border: 2px solid #007bff;
        outline: none;
    }
    .send-button{
        position: absolute;
        right: 20px;
        bottom: 20px;
        background-color: #007bff;
        width: 40px;
        height: 40px;
        padding: 2px;
        border-radius: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
    }
    i{
        color: white; 
    }
</style>