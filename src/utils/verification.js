import apiService from '@/services/api';

export const VerificationService = {
  // 發送電子郵件驗證碼
  sendEmailVerification: async (email) => {
    return await apiService.verification.sendEmailVerification(email);
  },
  
  // 驗證電子郵件
  verifyEmail: async (code) => {
    return await apiService.verification.verifyEmail(code);
  },
  
  // 發送簡訊驗證碼
  sendPhoneVerification: async (phone) => {
    return await apiService.verification.sendPhoneVerification(phone);
  },
  
  // 驗證手機
  verifyPhone: async (code) => {
    return await apiService.verification.verifyPhone(code);
  }
};

export default VerificationService;