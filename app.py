import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# 모든 출처(Origin)에 대해 CORS 허용
CORS(app, resources={r"/*": {"origins": "*"}})

# Flask 라우팅 시 끝의 / 여부와 상관없이 매칭되도록 설정
app.url_map.strict_slashes = False

class Node:
    """이진 검색 트리의 노드 클래스"""
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

    def to_dict(self):
        """노드 및 하위 트리 구조를 JSON 직렬화 가능한 dict로 변환"""
        return {
            "key": self.key,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }


class BinarySearchTree:
    """이진 검색 트리 알고리즘 클래스"""
    def __init__(self):
        self.root = None

    def build_from_list(self, keys):
        """리스트 형태의 키 배열로부터 트리 구성"""
        self.root = None
        if not keys:
            return
        for k in keys:
            if isinstance(k, (int, float)):
                self.add(k)

    def search(self, key):
        """키 검색: 탐색 경로(path)와 발견 여부(found) 반환"""
        path = []
        curr = self.root
        while curr:
            path.append(curr.key)
            if key == curr.key:
                return True, path
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return False, path

    def add(self, key):
        """키 삽입: 단계별 탐색 경로 및 결과 메시지 반환"""
        steps = []
        if self.root is None:
            self.root = Node(key)
            steps.append({"key": key, "msg": f"루트 노드로 {key} 생성"})
            return steps

        curr = self.root
        while True:
            steps.append({"key": curr.key, "msg": f"노드 {curr.key}와 비교 중..."})
            if key == curr.key:
                steps.append({"key": curr.key, "msg": f"키 {key} 이미 존재함 (중복 불가)"})
                break
            elif key < curr.key:
                if curr.left is None:
                    curr.left = Node(key)
                    steps.append({"key": key, "msg": f"노드 {curr.key}의 왼쪽에 {key} 삽입 완료"})
                    break
                curr = curr.left
            else:
                if curr.right is None:
                    curr.right = Node(key)
                    steps.append({"key": key, "msg": f"노드 {curr.key}의 오른쪽에 {key} 삽입 완료"})
                    break
                curr = curr.right
        return steps

    def remove(self, key):
        """키 삭제: 단계별 진행 과정 및 성공 여부 반환"""
        steps = []
        
        def _delete_node(root, key):
            if root is None:
                steps.append({"key": None, "msg": f"키 {key}를 찾을 수 없음"})
                return root, False

            steps.append({"key": root.key, "msg": f"노드 {root.key} 검사 중..."})

            if key < root.key:
                root.left, deleted = _delete_node(root.left, key)
                return root, deleted
            elif key > root.key:
                root.right, deleted = _delete_node(root.right, key)
                return root, deleted
            else:
                steps.append({"key": root.key, "msg": f"삭제할 노드 {root.key} 발견!"})
                # 자식이 없거나 1개인 경우
                if root.left is None:
                    return root.right, True
                elif root.right is None:
                    return root.left, True

                # 자식이 2개인 경우: 오른쪽 서브트리의 최소값(In-order successor) 찾기
                succ = root.right
                while succ.left:
                    succ = succ.left
                steps.append({"key": succ.key, "msg": f"오른쪽 서브트리의 후계자 노드 {succ.key} 선택"})
                root.key = succ.key
                root.right, _ = _delete_node(root.right, succ.key)
                return root, True

        self.root, success = _delete_node(self.root, key)
        return steps, success

    def dump(self):
        """중위 순회(In-Order Traversal)하여 정렬된 키 리스트 반환"""
        result = []
        def _inorder(node):
            if node:
                _inorder(node.left)
                result.append(node.key)
                _inorder(node.right)
        _inorder(self.root)
        return result

    def min_key(self):
        """최소 키 및 해당 노드까지의 탐색 경로 반환"""
        if not self.root:
            return None, []
        path = []
        curr = self.root
        while curr:
            path.append(curr.key)
            if curr.left is None:
                return curr.key, path
            curr = curr.left

    def max_key(self):
        """최대 키 및 해당 노드까지의 탐색 경로 반환"""
        if not self.root:
            return None, []
        path = []
        curr = self.root
        while curr:
            path.append(curr.key)
            if curr.right is None:
                return curr.key, path
            curr = curr.right


@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
@app.route('/api/bst', methods=['GET', 'POST', 'OPTIONS'])
def handle_bst_request():
    """BST 연동 통합 API 엔드포인트 (POST, GET, OPTIONS 모두 지원)"""
    # CORS Preflight 대응
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    # GET 요청 시 헬스체크 응답
    if request.method == 'GET':
        return jsonify({
            'status': 'online',
            'message': 'Binary Search Tree Cloud Run Service is active. Send POST requests for operations.'
        }), 200

    start_time = time.time()
    data = request.get_json(silent=True) or {}

    action = data.get('action', 'dump')
    tree_data = data.get('treeData', [50, 30, 70, 20, 40, 60, 80])
    key = data.get('key', None)

    # BST 객체 생성 및 기존 데이터 로드
    bst = BinarySearchTree()
    bst.build_from_list(tree_data)

    response_data = {
        'success': True,
        'action': action,
        'input_key': key
    }

    if action == 'add':
        if key is None:
            response_data['success'] = False
            response_data['error'] = '삽입할 키(key) 값이 입력되지 않았습니다.'
        else:
            steps = bst.add(int(key))
            response_data['steps'] = steps
            response_data['message'] = f'키 {key} 삽입 연산이 완료되었습니다.'

    elif action == 'remove':
        if key is None:
            response_data['success'] = False
            response_data['error'] = '삭제할 키(key) 값이 입력되지 않았습니다.'
        else:
            steps, success = bst.remove(int(key))
            response_data['steps'] = steps
            response_data['found'] = success
            response_data['message'] = f'키 {key} 삭제 연산이 완료되었습니다.' if success else f'키 {key}를 찾을 수 없습니다.'

    elif action == 'search':
        if key is None:
            response_data['success'] = False
            response_data['error'] = '검색할 키(key) 값이 입력되지 않았습니다.'
        else:
            found, path = bst.search(int(key))
            response_data['found'] = found
            response_data['path'] = path
            response_data['message'] = f'키 {key} 탐색 완료 (존재 여부: {found})'

    elif action == 'range':
        min_v, min_p = bst.min_key()
        max_v, max_p = bst.max_key()
        response_data['min'] = min_v
        response_data['max'] = max_v
        response_data['min_path'] = min_p
        response_data['max_path'] = max_p
        response_data['message'] = f'트리의 최소값: {min_v}, 최대값: {max_v}'

    elif action == 'dump':
        dump_list = bst.dump()
        response_data['dump'] = dump_list
        response_data['message'] = f'In-Order Dump 연산 완료 (총 {len(dump_list)}개 노드)'

    else:
        response_data['success'] = False
        response_data['error'] = f'알 수 없는 연산(action): {action}'

    # 최신 트리 상태 및 구조 동기화
    response_data['updated_tree'] = bst.dump()
    response_data['tree_structure'] = bst.root.to_dict() if bst.root else None
    response_data['execution_time'] = f"{(time.time() - start_time) * 1000:.2f}ms"

    return jsonify(response_data), 200


@app.errorhandler(405)
def method_not_allowed(e):
    """405 발생 시에도 자동으로 POST 매칭을 유도하여 JSON 반환"""
    return jsonify({
        'success': False,
        'error': '405 Method Not Allowed: POST 방식을 사용하여 요청하세요.',
        'hint': 'Cloud Run URL 뒤에 /api/bst 경로를 명시했는지 확인하세요.'
    }), 405


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
