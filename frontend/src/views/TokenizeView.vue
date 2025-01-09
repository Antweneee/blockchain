<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="bg-white rounded-lg shadow-sm p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Tokenize New Asset</h1>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Asset Information -->
        <div>
          <h2 class="text-lg font-medium text-gray-900 mb-4">Asset Information</h2>

          <div class="space-y-4">
            <div>
              <label for="title" class="block text-sm font-medium text-gray-700">
                Asset Title
              </label>
              <input
                id="title"
                v-model="form.title"
                type="text"
                required
                class="input-field"
                placeholder="Enter asset title"
              >
            </div>

            <div>
              <label for="description" class="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                v-model="form.description"
                rows="4"
                required
                class="input-field"
                placeholder="Describe your asset"
              ></textarea>
            </div>

            <div>
              <label for="transferFee" class="block text-sm font-medium text-gray-700">
                Transfer Fee (%)
              </label>
              <input
                id="transferFee"
                v-model="form.transferFee"
                type="number"
                step="0.1"
                min="0"
                max="50"
                class="input-field"
                placeholder="Enter transfer fee percentage (0-50%)"
              >
              <p class="mt-1 text-sm text-gray-500">
                Optional: Set a royalty percentage for future transfers (0-50%)
              </p>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">
                Asset Image
              </label>
              <div
                class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md cursor-pointer"
                :class="{ 'border-primary': isDragging }"
                @click="fileInput.click()"
                @dragenter.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @dragover.prevent
                @drop.prevent="handleDrop"
              >
                <div class="space-y-1 text-center">
                  <div v-if="!form.imagePreview" class="flex flex-col items-center">
                    <svg
                      class="mx-auto h-12 w-12 text-gray-400"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    <p class="mt-1 text-sm text-gray-600">
                      Drag and drop or click to select
                    </p>
                  </div>
                  <div v-else class="relative">
                    <img
                      :src="form.imagePreview"
                      alt="Asset preview"
                      class="max-h-48 rounded-md"
                    >
                    <button
                      type="button"
                      @click.stop="removeImage"
                      class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                    >
                      ×
                    </button>
                  </div>
                  <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileSelect"
                    accept="image/*"
                    class="hidden"
                  >
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Legal Information -->
        <div class="pt-6 border-t border-gray-200">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Legal Information</h2>

          <div class="space-y-4">
            <div class="flex items-start">
              <div class="flex items-center h-5">
                <input
                  id="terms"
                  v-model="form.acceptedTerms"
                  type="checkbox"
                  required
                  class="h-4 w-4 text-primary border-gray-300 rounded"
                >
              </div>
              <div class="ml-3 text-sm">
                <label for="terms" class="font-medium text-gray-700">
                  I confirm that I own or have the rights to tokenize this asset
                </label>
                <p class="text-gray-500">
                  By proceeding, you confirm that you own or have the necessary rights to tokenize this asset on the XRP Ledger.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex justify-end pt-6 border-t border-gray-200">
          <button
            type="submit"
            class="btn-primary"
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting">
              Tokenizing...
            </span>
            <span v-else>
              Create Token
            </span>
          </button>
        </div>
      </form>
    </div>

    <!-- Upload Progress Modal -->
    <div v-if="showProgress" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Creating Asset Token</h3>
        <div class="space-y-4">
          <div v-for="(step, index) in progressSteps" :key="index" class="flex items-center">
            <div :class="[
              'flex-shrink-0 h-6 w-6 rounded-full flex items-center justify-center',
              step.completed ? 'bg-green-100 text-green-600' :
              step.current ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
            ]">
              <span v-if="step.completed">✓</span>
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span class="ml-3 text-sm text-gray-600">{{ step.label }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useMarketplaceStore } from '../store'
import axios from 'axios'

const router = useRouter()
const marketplaceStore = useMarketplaceStore()
const fileInput = ref(null)
const isDragging = ref(false)
const isSubmitting = ref(false)
const showProgress = ref(false)

const form = reactive({
  title: '',
  description: '',
  transferFee: 0,
  imageFile: null,
  imagePreview: null,
  acceptedTerms: false
})

const progressSteps = reactive([
  { label: 'Uploading image', completed: false, current: true },
  { label: 'Creating NFT on XRPL', completed: false, current: false }
])

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  form.imageFile = file
  const reader = new FileReader()
  reader.onload = (e) => {
    form.imagePreview = e.target.result
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  form.imageFile = null
  form.imagePreview = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleSubmit = async () => {
  if (isSubmitting.value) return

  try {
    isSubmitting.value = true
    showProgress.value = true

    const formData = new FormData()
    formData.append('image', form.imageFile)
    progressSteps[0].current = true

    const uploadResponse = await axios.post('/api/upload', formData)
    progressSteps[0].completed = true
    progressSteps[0].current = false
    progressSteps[1].current = true

    const assetResponse = await axios.post('/api/assets', {
      title: form.title,
      description: form.description,
      metadata_url: uploadResponse.data.metadata_url,
      transfer_fee: parseFloat(form.transferFee)
    })
    progressSteps[1].completed = true
    progressSteps[1].current = false

    router.push(`/asset-details/${assetResponse.data.asset.id}`)

  } catch (error) {
    console.error('Failed to tokenize asset:', error.response || error)
    alert('An error occurred while tokenizing the asset. Please try again.')
  } finally {
    isSubmitting.value = false
    showProgress.value = false
  }
}
</script>
