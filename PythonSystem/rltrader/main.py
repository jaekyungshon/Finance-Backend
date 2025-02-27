import os
import sys
import logging
import argparse
import json
import settings
import utils
import data_manager


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['train', 'test', 'update', 'predict'], default='train') # 모델 모드
    parser.add_argument('--ver', choices=['v1', 'v2', 'v3', 'v4', 'v4.1', 'v4.2'], default='v1') # 데이터 버전
    parser.add_argument('--name', default=utils.get_time_str()) # 날짜
    parser.add_argument('--stock_code', nargs='+') # 종목코드
    parser.add_argument('--rl_method', choices=['dqn', 'pg', 'ac', 'a2c', 'a3c', 'ppo', 'monkey'], default='a2c') # 강화학습 기법
    parser.add_argument('--net', choices=['dnn', 'lstm', 'cnn', 'monkey'], default='dnn') # 신경망
    parser.add_argument('--backend', choices=['pytorch', 'tensorflow', 'plaidml'], default='tensorflow') # 딥러닝 라이브러리
    parser.add_argument('--start_date', default='20220101') # 데이터 시작일
    parser.add_argument('--end_date', default=utils.get_today_str()) # 데이터 종료일
    parser.add_argument('--lr', type=float, default=0.001) # 학습율
    parser.add_argument('--discount_factor', type=float, default=0.99) # 지연보상율
    parser.add_argument('--balance', type=int, default=100000000) # 매매 초기 자금
    args = parser.parse_args()

    # 학습기 파라미터 설정
    output_name = f'{args.mode}_{args.name}_{args.rl_method}_{args.net}' # 학습 결과 출력 폴더명
    learning = args.mode in ['train', 'update'] # 모델 모드
    reuse_models = args.mode in ['test', 'update', 'predict'] # 기존 모델 
    value_network_name = f'{args.name}_{args.rl_method}_{args.net}_value.mdl' # 가치 신경망
    policy_network_name = f'{args.name}_{args.rl_method}_{args.net}_policy.mdl' # 정책 신경망
    #value_network_name=f'{args.name}_{args.rl_method}_{args.net}_value.h5'
    #policy_network_name=f'{args.name}_{args.rl_method}_{args.net}_policy.h5'
    start_epsilon = 1 if args.mode in ['train', 'update'] else 0 # 무작위 탐험율
    num_epoches = 2 if args.mode in ['train', 'update'] else 1 # 탐험수: 임의 조정으로 탐험수 조절 가능
    num_steps = 5 if args.net in ['lstm', 'cnn'] else 1 # 노드 건너뛰기 수

    # Backend 설정
    

    # 출력 경로 생성
    output_path = os.path.join(settings.BASE_DIR, 'output', output_name)
    if not os.path.isdir(output_path):
        os.makedirs(output_path)

    # 파라미터 기록
    params = json.dumps(vars(args))
    with open(os.path.join(output_path, 'params.json'), 'w') as f:
        f.write(params)

    # 모델 경로 준비
    # 모델 포멧은 TensorFlow는 h5, PyTorch는 pickle
    value_network_path = os.path.join(settings.BASE_DIR, 'models', value_network_name)
    policy_network_path = os.path.join(settings.BASE_DIR, 'models', policy_network_name)
    #value_network_path=f"D:\\학교\\학교개인프로젝트모음\\rltrader\\models\\"+value_network_name
    #policy_network_path=f"D:\\학교\\학교개인프로젝트모음\\rltrader\\models\\"+policy_network_name

    # 로그 기록 설정
    log_path = os.path.join(output_path, f'{output_name}.log')
    if os.path.exists(log_path):
        os.remove(log_path)
    logging.basicConfig(format='%(message)s')
    logger = logging.getLogger(settings.LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(filename=log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.info(params)
    
    # Backend 설정, 로그 설정을 먼저하고 RLTrader 모듈들을 이후에 임포트해야 함
    from learners import ReinforcementLearner, DQNLearner, \
        PolicyGradientLearner, ActorCriticLearner, A2CLearner, A3CLearner, PPOLearner

    common_params = {}
    list_stock_code = []
    list_chart_data = []
    list_training_data = []
    list_min_trading_price = []
    list_max_trading_price = []

    for stock_code in args.stock_code:
        # 차트 데이터, 학습 데이터 준비
        chart_data, training_data = data_manager.load_data(
            stock_code, args.start_date, args.end_date, ver=args.ver)

        assert len(chart_data) >= num_steps
        
        # 최소/최대 단일 매매 금액 설정
        min_trading_price = 100000
        max_trading_price = 10000000

        # 공통 파라미터 설정
        common_params = {'rl_method': args.rl_method, 
            'net': args.net, 'num_steps': num_steps, 'lr': args.lr,
            'balance': args.balance, 'num_epoches': num_epoches, 
            'discount_factor': args.discount_factor, 'start_epsilon': start_epsilon,
            'output_path': output_path, 'reuse_models': reuse_models}

        # 강화학습 시작
        learner = None
        if args.rl_method != 'a3c':
            common_params.update({'stock_code': stock_code,
                'chart_data': chart_data, 
                'training_data': training_data,
                'min_trading_price': min_trading_price, 
                'max_trading_price': max_trading_price})
            if args.rl_method == 'dqn':
                learner = DQNLearner(**{**common_params, 
                    'value_network_path': value_network_path})
            elif args.rl_method == 'pg':
                learner = PolicyGradientLearner(**{**common_params, 
                    'policy_network_path': policy_network_path})
            elif args.rl_method == 'ac':
                learner = ActorCriticLearner(**{**common_params, 
                    'value_network_path': value_network_path, 
                    'policy_network_path': policy_network_path})
            elif args.rl_method == 'a2c':
                learner = A2CLearner(**{**common_params, 
                    'value_network_path': value_network_path, 
                    'policy_network_path': policy_network_path})
            elif args.rl_method == 'ppo':
                learner = PPOLearner(**{**common_params, 
                    'value_network_path': value_network_path, 
                    'policy_network_path': policy_network_path})
            elif args.rl_method == 'monkey':
                common_params['net'] = args.rl_method
                common_params['num_epoches'] = 10
                common_params['start_epsilon'] = 1
                learning = False
                learner = ReinforcementLearner(**common_params)
        else:
            list_stock_code.append(stock_code)
            list_chart_data.append(chart_data)
            list_training_data.append(training_data)
            list_min_trading_price.append(min_trading_price)
            list_max_trading_price.append(max_trading_price)

    if args.rl_method == 'a3c':
        learner = A3CLearner(**{
            **common_params, 
            'list_stock_code': list_stock_code, 
            'list_chart_data': list_chart_data, 
            'list_training_data': list_training_data,
            'list_min_trading_price': list_min_trading_price, 
            'list_max_trading_price': list_max_trading_price,
            'value_network_path': value_network_path, 
            'policy_network_path': policy_network_path})
    
    assert learner is not None

    ## 학습 시작 ##
    if args.mode in ['train', 'test', 'update']:
        ## 학습 run 코드 ##
        learner.run(learning=learning) # learners.py
        
        ## 시뮬레이션 후, 학습된 모델 저장 - 저장이 안되서 배제 ##
        #if args.mode in ['train', 'update']:
        #    learner.save_models()
    
    ## 시뮬레이션 중, PV값이 좋았던 epoch를 모델로 선택하여, 새로운 장에서 예측 ##
    # epoch가 마지막에 가까울수록, 가장 최근 시장까지 데이터 적용#
    # 주식장이 어떤 상황인지 파악하는데 어느 정도의 위험성 존재 #
    elif args.mode == 'predict':
        learner.predict()
                