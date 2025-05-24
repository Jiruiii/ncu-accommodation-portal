<template>
    <div class="chatroom-flame">
        <div class="chatroom-title">
            <div class="chat-person">
                <img class="landlord-image" src="https://randomuser.me/api/portraits/men/42.jpg" />
                <div class="landlord-name">張先生</div>
            </div>
            <i class="fa-solid fa-phone" style="color: black; font-size: 25px; cursor: pointer;"></i>
        </div>
        <div class="chatroom" ref="chatContainer">
            <template v-if="checkmsg_tenant">
                <div class="msg-tenant" v-for="(msgTenant, index) in msgsTenant" :key="'tenant-' + index">
                    <div class="time">{{msgTenant.time}}</div>
                    <div class="message-tenant">{{msgTenant.msg}}</div>
                    <img class="msg-tenant-image"  src="https://randomuser.me/api/portraits/women/65.jpg" />
                </div>
            </template>
            <template v-if="checkmsg_receive">
                <div class="msg-landlord" v-for="(msgReceive, index) in msgsReceive" :key="'landlord-' + index">
                    <img class="msg-landlord-image" src="https://randomuser.me/api/portraits/men/42.jpg" />
                    <div class="message-landlord">{{msgReceive.msg_receive}}</div>
                    <div class="time">{{msgReceive.time_receive}}</div>
                </div>
            </template>
        </div>
        <div class="input-flame">
            <input placeholder="請輸入文字..." v-model.trim="msg" @keydown.enter="addMessages"/>
            <div class="send-button" @click="addMessages"><i class="fa-solid fa-paper-plane"></i></div>
        </div>
    </div>
</template>

<script>
    import { ref, onMounted, nextTick } from "vue";
    // import { useRouter } from "vue-router";
    import apiService from "@/services/api";
    import { io } from "socket.io-client";

    export default{
        name: "ChatRoom",
        setup (){
            // const router = useRouter();
            const msgsTenant = ref([]);
            const msg = ref("");
            const time = ref("");
            const checkmsg_tenant = ref(false);
            const checkmsg_receive = ref(false);
            const chatContainer = ref(null);
            const jsonData = ref(null);
            const user = ref([]); 
            const userId = ref(8);
            const msgsReceive = ref([]);
            const msg_receive = ref("");
            const time_receive = ref("");
            const targetUserId = ref(9);

            // 添加訊息
            const addMessages = () => {
                time.value = new Date(); // 獲取時間
                msgsTenant.value.push({ 
                    msg: msg.value, 
                    time: new Intl.DateTimeFormat("zh-TW", {
                        hour: "numeric",
                        minute: "numeric",
                        second: undefined,
                        hour12: true,  // 讓時間顯示為 12 小時制（上午/下午）
                        timeZone: "Asia/Taipei"
                    }).format(time.value)
                });

                msg.value = "";  // 清空輸入框

                checkMessageTenant(); 

                //navigateMessages();

                sendMessage();

                // 有新訊息自動滾動到底部 
                nextTick(() => {
                    if (chatContainer.value) {
                        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                    }
                });  
            };

            // 確認是否有訊息
            const checkMessageTenant = () => {
                checkmsg_tenant.value = msgsTenant.value.length > 0;
            };

            // 確認是否有訊息傳入
            const checkMessageReceive = () => {
                checkmsg_receive.value = msgsReceive.value.length > 0;
            };

            // 將新訊息傳遞到後端
            /*const navigateMessages = () => {
                if (msgsTenant.value.length > 0) {
                    const latestMsg = msgsTenant.value[msgsTenant.value.length - 1].msg;
                    const latestTime = new Intl.DateTimeFormat("zh-TW", {
                        hour: "numeric",
                        minute: "numeric",
                        hour12: true
                    }).format(new Date());

                    // 發送 API 請求
                    fetch("http://localhost:5000/api/chat", {
                        method: "POST",
                        mode: "cors",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ 
                            message: latestMsg, 
                            time: latestTime
                        })
                    })
                    .then(res => res.json())
                    .then(data => console.log("後端回應：", data)) 
                    .catch(err => console.error("請求失敗", err));

                    console.log("訊息已送到後端:", latestMsg, latestTime);
                } else {
                    console.warn("沒有可推送的訊息！");
                }
            };*/

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
                console.log(`收到來自 ${data.sender} 的訊息:`, data.message);

                msgsReceive.value.push({ 
                    msg_receive: data.message, 
                    time_receive: new Intl.DateTimeFormat("zh-TW", {
                        hour: "numeric",
                        minute: "numeric",
                        second: undefined,
                        hour12: true,  // 顯示上午/下午
                        timeZone: "Asia/Taipei"
                    }).format(new Date())
                });

                // 有新訊息自動滾動到底部
                nextTick(() => {
                    if (chatContainer.value) {
                        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                    }
                });

                checkMessageTenant();  
            });

            // 發送訊息給其他用戶
            const sendMessage = () => {
                const latestMsg = msgsTenant.value[msgsTenant.value.length - 1].msg;
                const latesTime = new Date();

                console.log("送出訊息:", latestMsg);  
                socket.emit("new_message", { sender: userId.value, receiver: targetUserId.value, message: latestMsg, time: latesTime });
            };

            // 取德用戶的 id
            const fetchData = async () => {
                try {
                    const response = await apiService.users.getProfile();
                    user.value = response.user;

                    userId.value = user.value.user_id;
                    console.log("獲取的 ID:", userId.value);
                } catch (error) {
                    console.error("讀取 JSON 失敗:", error);
                }
            };

            const fetchHistory = async () => {
                try {
                    const response = await fetch(`http://localhost:5000/api/chat/history?sender_id=${userId.value}&receiver_id=${targetUserId.value}`);
                    const history = await response.json();
                    
                    msgsTenant.value = history.map(msg => {
                        const formattedTime = new Intl.DateTimeFormat("zh-TW", {
                            hour: "numeric",
                            minute: "numeric",
                            hour12: true,
                            timeZone: "Asia/Taipei"
                        }).format(new Date(msg.timestamp));

                        return {
                            msg: msg.text,
                            time: formattedTime
                                .replace("AM", "上午")
                                .replace("PM", "下午")
                        };
                    });

                    checkMessageTenant();  // 確保更新 UI 狀態
                } catch (error) {
                    console.error("獲取歷史訊息失敗:", error);
                }
            };

            onMounted(async () => {
                // 先移除所有舊的監聽，避免累積事件
                socket.off("new_message"); 

                await fetchData(); // 確保先取得 userId
                await fetchHistory();

                nextTick(() => {
                    if (chatContainer.value) {
                        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
                    }
                });
            }); 

            return { 
                msgsTenant,
                msg,
                time,
                checkmsg_tenant,
                addMessages,
                checkMessageTenant,
                checkMessageReceive,
                chatContainer,
                //navigateMessages,
                jsonData,
                user,
                userId,
                msgsReceive,
                msg_receive,
                time_receive,
                checkmsg_receive,
                targetUserId,
                fetchHistory,
            };
        },
    }
</script>

<style scoped>
    .chatroom-flame{
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
        background-color: #D0D0D0;
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
        height: 80px;
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