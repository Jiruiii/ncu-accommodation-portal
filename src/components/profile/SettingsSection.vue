<template>
  <div class="settings-section">
    <h3 v-if="title">{{ title }}</h3>
    <slot></slot>
  </div>
</template>

<script>
  export default {
    name: "SettingsSection",
    props: {
      title: {
        type: String,
        default: "",
      },
    },
  };
</script>

<style scoped>
  .settings-section {
    margin-bottom: 30px;
    padding-bottom: 20px;
  }

  h3 {
    font-size: 1.2rem;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eaeaea;
    color: #333;
  }
</style>
