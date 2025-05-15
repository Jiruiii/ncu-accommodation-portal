<template>
  <div class="verification-code-input">
    <input
      :value="modelValue"
      @input="updateValue($event)"
      :placeholder="placeholder"
      :maxlength="maxLength"
      @keypress="validateInput"
      class="code-input"
    />
  </div>
</template>
  
<script>
export default {
  name: "VerificationCodeInput",
  props: {
    modelValue: {
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
  emits: ["update:modelValue"],  
  methods: {
    updateValue(event) {
      const value = event.target.value.replace(/[^0-9]/g, '');
      this.$emit("update:modelValue", value);
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
  
.code-input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  text-align: center;
  letter-spacing: 5px;
  border: 2px solid #ddd;
  border-radius: 8px;
}

.code-input:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 5px rgba(74, 144, 226, 0.5);
}
</style>