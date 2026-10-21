from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

app = Flask(__name__)
# 모든 오리진에 대한 CORS 설정 (GAS 및 웹 응용 프로그램과의 통신을 허용)
CORS(app, resources={r"/*": {"origins": "*"}})

class Node:
    """
    이진 검색 트리의 노드를 나타내는 클래스
    """
    def __init__(self, key, value=None, left=None, right=None):
        self.key = key          # 노드의 키 값 (비교 기준)
        self.value = value if value is not None else key  # 데이터 값
        self.left = left        # 왼쪽 자식 노드 참조
        self.right = right      # 오른쪽 자식 노드 참조

    def to_dict(self):
        """
        클라이언트로 JSON 형태로 전송하기 위한 노드 객체 변환 메서드
        """
        return {
            'key': self.key,
            'value': self.value,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None
        }

class BinarySearchTree:
    """
    이진 검색 트리(BST) 알고리즘을 구현한 클래스
    """
    def __init__(self):
        self.root = None  # 트리의 루트 노드 초기화

    def search(self, key):
        """
        특정 키를 검색하는 메서드 및 단계별 검색 경로 추적
        """
        path = []
        ptr = self.root
        while ptr is not None:
            path.append(ptr.key)
            if key == ptr.key:
                return ptr, path, True  # 찾았음
            elif key < ptr.key:
                ptr = ptr.left
            else:
                ptr = ptr.right
        return None, path, False  # 찾지 못함

    def add(self, key, value=None):
        """
        새로운 키-값을 트리에 삽입하는 메서드
        """
        if value is None:
            value = key

        steps = []  # 탐색 과정 기록

        def _add_node(node, key, value):
            if node is None:
                steps.append({"type": "create", "key": key, "msg": f"새 노드 {key} 생성"})
                return Node(key, value)

            steps.append({"type": "visit", "key": node.key, "msg": f"노드 {node.key} 방문 및 비교"})

            if key == node.key:
                steps.append({"type": "duplicate", "key": key, "msg": f"키 {key} 이미 존재함 (삽입 실패)"})
                return node  # 중복 키 허용 안 함
            elif key < node.key:
                steps.append({"type": "move_left", "key": node.key, "msg": f"{key} < {node.key}: 왼쪽으로 이동"})
                node.left = _add_node(node.left, key, value)
            else:
                steps.append({"type": "move_right", "key": node.key, "msg": f"{key} > {node.key}: 오른쪽으로 이동"})
                node.right = _add_node(node.right, key, value)
            
            return node

        if self.root is None:
            self.root = Node(key, value)
            steps.append({"type": "create_root", "key": key, "msg": f"루트 노드 {key} 생성"})
            return True, steps

        self.root = _add_node(self.root, key, value)
        return True, steps

    def remove(self, key):
        """
        트리에서 특정 키의 노드를 삭제하는 메서드
        """
        steps = []
        deleted = False

        def _remove_node(node, key):
            nonlocal deleted
            if node is None:
                steps.append({"type": "not_found", "key": key, "msg": f"키 {key}를 찾을 수 없음"})
                return None

            steps.append({"type": "visit", "key": node.key, "msg": f"노드 {node.key} 방문"})

            if key < node.key:
                steps.append({"type": "move_left", "key": node.key, "msg": f"{key} < {node.key}: 왼쪽 탐색"})
                node.left = _remove_node(node.left, key)
            elif key > node.key:
                steps.append({"type": "move_right", "key": node.key, "msg": f"{key} > {node.key}: 오른쪽 탐색"})
                node.right = _remove_node(node.right, key)
            else:
                # 삭제 대상 노드 발견
                deleted = True
                steps.append({"type": "found", "key": node.key, "msg": f"삭제할 노드 {node.key} 발견"})

                # Case 1: 자식이 없는 경우 (리프 노드)
                if node.left is None and node.right is None:
                    steps.append({"type": "remove_leaf", "key": node.key, "msg": f"리프 노드 {node.key} 제거"})
                    return None

                # Case 2: 오른쪽 자식만 있는 경우
                if node.left is None:
                    steps.append({"type": "replace_right", "key": node.key, "msg": f"노드 {node.key}를 오른쪽 자식으로 대체"})
                    return node.right

                # Case 3: 왼쪽 자식만 있는 경우
                if node.right is None:
                    steps.append({"type": "replace_left", "key": node.key, "msg": f"노드 {node.key}를 왼쪽 자식으로 대체"})
                    return node.left

                # Case 4: 두 자식이 모두 있는 경우 (왼쪽 서브트리의 최대값으로 대체)
                steps.append({"type": "find_successor", "key": node.key, "msg": f"왼쪽 서브트리에서 가장 큰 노드 검색 시작"})
                max_left = self._max_node(node.left)
                steps.append({"type": "swap", "key": node.key, "replace_with": max_left.key, "msg": f"노드 {node.key}를 왼쪽 최대값 {max_left.key}로 교체"})
                node.key = max_left.key
                node.value = max_left.value
                node.left = _remove_node(node.left, max_left.key)

            return node

        self.root = _remove_node(self.root, key)
        return deleted, steps

    def _max_node(self, node):
        """서브트리에서 최대 키 값을 가진 노드 찾기"""
        ptr = node
        while ptr.right is not None:
            ptr = ptr.right
        return ptr

    def dump(self):
        """
        트리의 모든 노드를 중위 순회(In-Order Traversal)하여 정렬된 순서로 반환
        """
        result = []
        def _inorder(node):
            if node is not None:
                _inorder(node.left)
                result.append({"key": node.key, "value": node.value})
                _inorder(node.right)
        
        _inorder(self.root)
        return result

    def min_key(self):
        """최소 키 값 검색"""
        if self.root is None:
            return None
        ptr = self.root
        path = []
        while ptr.left is not None:
            path.append(ptr.key)
            ptr = ptr.left
        path.append(ptr.key)
        return ptr.key, path

    def max_key(self):
        """최대 키 값 검색"""
        if self.root is None:
            return None
        ptr = self.root
        path = []
        while ptr.right is not None:
            path.append(ptr.key)
            ptr = ptr.right
        path.append(ptr.key)
        return ptr.key, path

def build_tree_from_list(items):
    """배열 데이터로부터 BST 구축"""
    bst = BinarySearchTree()
    for item in items:
        if isinstance(item, dict):
            bst.add(item.get('key'), item.get('value'))
        else:
            bst.add(int(item))
    return bst

@app.route('/', methods=['GET'])
def health_check():
    """헬스 체크 및 기본 상태 반환"""
    return jsonify({"status": "healthy", "service": "BST Cloud Run API Engine"}), 200

@app.route('/api/bst', methods=['POST'])
def handle_bst_operations():
    """
    BST 알고리즘 통합 처리 API 엔드포인트
    """
    try:
        data = request.get_json() or {}
        action = data.get('action', 'dump')
        tree_data = data.get('treeData', [50, 30, 70, 20, 40, 60, 80])
        key = data.get('key')
        
        if key is not None:
            try:
                key = int(key)
            except ValueError:
                pass

        # 요청받은 트리 상태로 BST 객체 구성
        bst = build_tree_from_list(tree_data)

        response = {
            "success": True,
            "action": action,
            "initial_tree": [n['key'] for n in bst.dump()]
        }

        # 1. SEARCH (검색)
        if action == 'search':
            if key is None:
                return jsonify({"success": False, "error": "검색할 키가 제공되지 않았습니다."}), 400
            found_node, path, is_found = bst.search(key)
            response.update({
                "found": is_found,
                "key": key,
                "path": path,
                "message": f"키 {key}를 찾았습니다." if is_found else f"키 {key}가 트리에 존재하지 않습니다."
            })

        # 2. ADD (삽입)
        elif action == 'add':
            if key is None:
                return jsonify({"success": False, "error": "삽입할 키가 제공되지 않았습니다."}), 400
            success, steps = bst.add(key)
            response.update({
                "inserted": success,
                "key": key,
                "steps": steps,
                "message": f"키 {key}가 성공적으로 추가되었습니다."
            })

        # 3. REMOVE (삭제)
        elif action == 'remove':
            if key is None:
                return jsonify({"success": False, "error": "삭제할 키가 제공되지 않았습니다."}), 400
            deleted, steps = bst.remove(key)
            response.update({
                "deleted": deleted,
                "key": key,
                "steps": steps,
                "message": f"키 {key}가 삭제되었습니다." if deleted else f"키 {key}를 찾지 못해 삭제할 수 없습니다."
            })

        # 4. DUMP (덤프 - 중위 순회)
        elif action == 'dump':
            dump_data = bst.dump()
            response.update({
                "dump": dump_data,
                "message": f"트리 중위 순회 결과 (총 {len(dump_data)}개 노드)"
            })

        # 5. RANGE (최소값 및 최대값 범위 조회)
        elif action == 'range':
            min_res = bst.min_key()
            max_res = bst.max_key()
            response.update({
                "min": min_res[0] if min_res else None,
                "min_path": min_res[1] if min_res else [],
                "max": max_res[0] if max_res else None,
                "max_path": max_res[1] if max_res else [],
                "message": f"최소 키: {min_res[0] if min_res else 'None'}, 최대 키: {max_res[0] if max_res else 'None'}"
            })

        else:
            return jsonify({"success": False, "error": f"지원하지 않는 작업: {action}"}), 400

        # 작업 완료 후 변경된 트리 상태 포함
        response["updated_tree"] = bst.dump()
        response["tree_structure"] = bst.root.to_dict() if bst.root else None

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # 클라우드 런 포트 환경변수 기본값 설정 (PORT 8080)
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
