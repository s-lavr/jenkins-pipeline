def label = "mypod-${UUID.randomUUID().toString()}"


podTemplate(label: 'dockerbuild', yaml: """
apiVersion: v1
kind: Pod
metadata:
  name: dockerbuild
spec:
  containers:
    - name: docker
      image: docker
      command:
      - cat
      tty: true
      imagePullPolicy: Always
      env:
      - name: POD_IP
        valueFrom:
          fieldRef:
            fieldPath: status.podIP
      - name: DOCKER_HOST
        value: tcp://localhost:2375
    - name: dind
      image: docker:18.05-dind
      securityContext:
        privileged: true
      volumeMounts:
        - name: dind-storage
          mountPath: /var/lib/docker
  volumes:
    - name: dind-storage
      emptyDir: {}
"""
) {



    node ('dockerbuild') {

      stage ('Build Dockerfile and push image') {
        container('docker') {
          git url: 'https://github.com/s-lavr/jenkins-pipeline.git', branch: 'master'
          withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'f74f60fe-bc38-4b3e-ab91-d7af3416231e',
                            usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASSWORD']]) {

          sh '''
            docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
            docker build -t serglavr/hello:${BUILD_TAG} .
            docker push serglavr/hello:${BUILD_TAG}
          '''

          }
        }
      }


    }
}

podTemplate(label: 'deploytest', yaml: """
apiVersion: v1
kind: Pod
metadata:
  name: deploytest
spec:
  containers:
    - name: application
      image: serglavr/hello:${BUILD_TAG}
      ports:
      - name: http-port
        containerPort: 80
    - name: curl
      image: appropriate/curl
      command:
      - cat
      tty: true
"""
) {
    node ('deploytest') {
      stage ('Test application') {
        container('curl') {
        sh 'curl localhost:80'
        }
      }
    }
  }



podTemplate(label: 'deploy', yaml: """
apiVersion: v1
kind: Pod
metadata:
labels:
  component: ci
spec:
  serviceAccountName: cd-jenkins
  containers:
  - name: kubectl
    image: lachlanevenson/k8s-kubectl
    command:
    - cat
    tty: true
    """
) {
    node ('deploy') {

      stage ('Deploy app') {
        container('kubectl') {
          sh """
            cat <<EOF > test.yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: hello-app
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: hello-app
    spec:
      containers:
        - name: application
          image: serglavr/hello:${BUILD_TAG}
          imagePullPolicy: Always
          ports:
          - name: http-port
            containerPort: 80

---

apiVersion: v1
kind: Service
metadata:
  name: hello-app
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: 80
  selector:
    app: hello-app

---

apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: application-ingress
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  rules:
  - host: application.serglavr.dnsabr.com
    http:
      paths:
      - path: /
        backend:
          serviceName: hello-app
          servicePort: 80

EOF

            kubectl apply -f test.yaml
          """
        }
      }

    }
}
