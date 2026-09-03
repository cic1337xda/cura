<template>
  <Teleport to="body">
    <div class="modal-overlay" v-if="dialogState.show" @click.self="handleCancel">
      <div class="modal" style="max-width: 440px; text-align: center;">
        <h2>{{ dialogState.title }}</h2>

        <template v-if="dialogState.type === 'image'">
          <div style="margin: 16px 0; border-radius: 16px; overflow: hidden; max-height: 320px; display: flex; align-items: center; justify-content: center; background: var(--bg-card-hover);">
            <img :src="dialogState.imageSrc" style="max-width: 100%; max-height: 320px; object-fit: contain;" />
          </div>
          <p style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">Use this photo?</p>
        </template>

        <p v-else style="font-size: 15px; color: var(--text-secondary); margin: 12px 0 20px;">{{ dialogState.message }}</p>

        <div style="display: flex; gap: 12px; justify-content: center;">
          <button v-if="dialogState.onCancel" class="btn btn-outline" @click="handleCancel">
            {{ dialogState.type === 'image' ? 'Retake' : 'Cancel' }}
          </button>
          <button class="btn" :class="dialogState.type === 'confirm' ? 'btn-danger' : ''" @click="dialogState.onConfirm?.()">
            {{ dialogState.type === 'image' ? 'Save Photo' : dialogState.type === 'confirm' ? (dialogState.confirmText || 'Delete') : 'OK' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useDialog } from '../composables/useDialog'
const { dialogState } = useDialog()

function handleCancel() {
  dialogState.value.onCancel?.()
}
</script>