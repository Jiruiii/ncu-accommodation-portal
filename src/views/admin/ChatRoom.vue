<template>
    <div class="chatroom-flame">
        <div class="chatroom-title">
            <div class="chat-person">
                <img class="landlord-image" src="https://randomuser.me/api/portraits/men/42.jpg" />
                <div class="landlord-name">張先生</div>
            </div>
            <i class="fa-solid fa-phone" style="color: black; font-size: 25px; cursor: pointer;"></i>
        </div>
        <div class="chatroom">
            <div class="msg-tenant">
                <div class="time">4:15</div>
                <div class="message-tenant">冷氣開機後無法正常製冷，可能是需要添加冷媒。</div>
                <img class="msg-tenant-image"  src="https://randomuser.me/api/portraits/women/65.jpg" />
            </div>
            <div class="msg-landlord">
                <img class="msg-landlord-image" src="https://randomuser.me/api/portraits/men/42.jpg" />
                <div class="message-landlord">已完成冷媒添加及系統清潔，冷氣已恢復正常運作。</div>
                <div class="time">5:15</div>
            </div>
            <div class="input-flame">
                <input placeholder="請輸入文字..." />
                <div class="send-button"><i class="fa-solid fa-paper-plane"></i></div>
            </div>
        </div>
    </div>
</template>

<script>
    export default{
        name: "ChatRoom",
    }
</script>

<style scoped>
    .chatroom-flame{
        background-color: white;
        padding: 30px; 
    }
    .chatroom-title{
        background-color: #84C1FF;
        padding: 20px;
        border-bottom: 2px solid white;
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
        height: 70%;
        background-color: #C4E1FF;
        padding-top: 20px;
        display: flex;
        justify-content: center;
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
        height: 100px;
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