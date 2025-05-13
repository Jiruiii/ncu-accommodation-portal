<template>
    <div class="verification-code-input">
      <input
        v-model="code"
        :placeholder="placeholder"
        :maxlength="maxLength"
        @input="updateCode"
        @keypress="validateInput"
      />
    </div>
  </template>
  
  <script>
  export default {
    name: "VerificationCodeInput",
    props: {
      value: {
        type: String,
        default: ""
      },
      placeholder: {
        type: String,
        default: "請輸入驗證碼"
      },
      maxLength: {
        type: Number,
        default: 6
      }
    },
    data() {
      return {
        code: this.value
      };
    },
    watch: {
      value(newValue) {
        this.code = newValue;
      }
    },
    methods: {
      updateCode(e) {
        this.$emit("input", e.target.value);
      },
      validateInput(e) {
        // 只允許輸入數字
        if (!/^\d*$/.test(e.key)) {
          e.preventDefault();
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .verification-code-input {
    margin: 20px 0;
  }
  
  .verification-code-input input {
    width: 100%;
    padding: 12px;
    font-size: 16px;
    text-align: center;
    letter-spacing: 5px;
    border: 2px solid #ddd;
    border-radius: 8px;
  }
  </style>