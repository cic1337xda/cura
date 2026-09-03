import { ref, createApp, h, Teleport } from 'vue'

const dialogState = ref({
  show: false,
  type: 'confirm', // 'confirm' | 'alert' | 'image'
  title: '',
  message: '',
  confirmText: '',
  imageSrc: '',
  onConfirm: null,
  onCancel: null,
})

export function useDialog() {
  function confirm(message, title = 'Confirm', confirmText = 'Delete') {
    return new Promise((resolve) => {
      dialogState.value = {
        show: true, type: 'confirm', title, message, confirmText,
        onConfirm: () => { dialogState.value.show = false; resolve(true) },
        onCancel: () => { dialogState.value.show = false; resolve(false) },
      }
    })
  }

  function alertMsg(message, title = 'Notice') {
    return new Promise((resolve) => {
      dialogState.value = {
        show: true, type: 'alert', title, message,
        onConfirm: () => { dialogState.value.show = false; resolve() },
        onCancel: null,
      }
    })
  }

  function previewImage(src, title = 'Preview Photo') {
    return new Promise((resolve) => {
      dialogState.value = {
        show: true, type: 'image', title, imageSrc: src,
        onConfirm: () => { dialogState.value.show = false; resolve(true) },
        onCancel: () => { dialogState.value.show = false; resolve(false) },
      }
    })
  }

  return { confirm, alertMsg, previewImage, dialogState }
}
