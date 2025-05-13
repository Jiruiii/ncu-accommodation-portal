<template>
    <div class="settings-item">
      <div class="settings-label">{{ label }}</div>
      <div class="settings-content">
        <slot></slot>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "SettingsItem",
    props: {
      label: {
        type: String,
        required: true
      }
    }
  };
  </script>
  
  <style scoped>
  .settings-item {
    display: flex;
    padding: 15px 0;
    border-bottom: 1px solid #f5f5f5;
  }
  
  .settings-label {
    width: 120px;
    font-weight: 500;
    color: #555;
    padding-top: 5px;
  }
  
  .settings-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  @media (max-width: 600px) {
    .settings-item {
      flex-direction: column;
      gap: 10px;
    }
    
    .settings-label {
      width: 100%;
    }
  }
  </style>