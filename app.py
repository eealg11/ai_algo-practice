// 구글 클라우드 런 서비스 URL (클라우드 런 배포 후 제공받은 실제 URL)
// 예: "https://bst-service-xxxxxx-uc.a.run.app" 또는 "https://bst-service-xxxxxx-uc.a.run.app/api/bst"
var CLOUD_RUN_URL = "https://bst-service-xxxxxx-uc.a.run.app";

/**
 * GET 요청 발생 시 HTML 메인 웹 브라우저 화면 출력
 */
function doGet(e) {
  return HtmlService.createTemplateFromFile('index')
    .evaluate()
    .setTitle('이진 검색 트리 (BST) 알고리즘 시각화 시스템')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * 클라이언트에서 호출하는 구글 앱스 스크립트 서버 측 함수
 * Cloud Run REST API로 요청을 전달하고 결과를 반환합니다.
 */
function processBstOperation(payload) {
  try {
    var targetUrl = CLOUD_RUN_URL.trim();
    
    // URL 끝에 슬래시(/)가 있다면 제거
    if (targetUrl.endsWith('/')) {
      targetUrl = targetUrl.slice(0, -1);
    }
    
    // HTTP POST 요청 옵션 구성
    var options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload),
      "muteHttpExceptions": true
    };
    
    var startTime = new Date().getTime();
    
    // Cloud Run 백엔드로 HTTP Fetch 실행
    var response = UrlFetchApp.fetch(targetUrl, options);
    var endTime = new Date().getTime();
    
    var responseCode = response.getResponseCode();
    var responseBody = response.getContentText();
    
    if (responseCode === 200) {
      var result = JSON.parse(responseBody);
      result.latency = (endTime - startTime) + "ms";
      return result;
    } else {
      return {
        "success": false,
        "error": "Cloud Run Server Error (Status: " + responseCode + "): " + responseBody,
        "latency": (endTime - startTime) + "ms"
      };
    }
  } catch (error) {
    return {
      "success": false,
      "error": "GAS 백엔드 처리 중 오류 발생: " + error.toString()
    };
  }
}
